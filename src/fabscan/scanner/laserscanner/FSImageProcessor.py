__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import math
import logging, os
import numpy as np
import scipy.ndimage
import cv2
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.lib.util.FSInject import inject
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface


class LinearLeastSquares2D(object):
    '''
    2D linear least squares using the hesse normal form:
        d = x*sin(theta) + y*cos(theta)
    which allows you to have vertical lines.
    '''

    def fit(self, data):
        data_mean = data.mean(axis=0)
        x0, y0 = data_mean
        if data.shape[0] > 2:  # over determined
            u, v, w = np.linalg.svd(data - data_mean)
            vec = w[0]
            theta = math.atan2(vec[0], vec[1])
        elif data.shape[0] == 2:  # well determined
            theta = math.atan2(data[1, 0] - data[0, 0], data[1, 1] - data[0, 1])
        theta = (theta + math.pi * 5 / 2) % (2 * math.pi)
        d = x0 * math.sin(theta) + y0 * math.cos(theta)
        return d, theta

    def residuals(self, model, data):
        d, theta = model
        dfit = data[:, 0] * math.sin(theta) + data[:, 1] * math.cos(theta)
        return np.abs(d - dfit)

    def is_degenerate(self, sample):
        return False


@inject(
    config=ConfigInterface,
    settings=SettingsInterface
)
class ImageProcessor(ImageProcessorInterface):

    def __init__(self, config, settings):

        self.settings = settings
        self.config = config
        self._logger = logging.getLogger(__name__)
        self.laser_color_channel = self.config.file.laser.color
        self.threshold_enable = False
        self.threshold_value = 0
        self.blur_enable = True
        self.blur_value = 0
        self.window_enable = False
        self.window_value = 0
        self.color = (255, 255, 255)
        self.refinement_method = 'SGF' #possible  RANSAC, SGF
        self.image_height = self.config.file.camera.resolution.width
        self.image_width = self.config.file.camera.resolution.height
        self.high_resolution = (self.config.file.camera.resolution.height, self.config.file.camera.resolution.width)
        self.preview_resolution = (self.config.file.camera.preview_resolution.height, self.config.file.camera.preview_resolution.width)

        #aruco.DICT_5X5_250
        # Note: Pattern generated using the following link
        # https://calib.io/pages/camera-calibration-pattern-generator
        self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
        self.charuco_board = cv2.aruco.CharucoBoard_create(11, 9, 1, 0.5, self.aruco_dict)

        self._full_res_weight_matrix = self._compute_weight_matrix(resolution=self.high_resolution)
        self._preview_res_weight_matrix = self._compute_weight_matrix(resolution=self.preview_resolution)

        self._criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.object_pattern_points = self.create_object_pattern_points()

    def get_aruco_board(self):
        return self.charuco_board

    def get_aruco_dict(self):
        return self.aruco_dict

    def _compute_weight_matrix(self, resolution):

        _weight_matrix = np.array(
            (np.matrix(np.linspace(0, resolution[0] - 1, resolution[0])).T *
             np.matrix(np.ones(resolution[1]))).T)
        return _weight_matrix

    def create_object_pattern_points(self):
        objp = np.zeros((self.config.file.calibration.pattern.rows * self.config.file.calibration.pattern.columns, 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.config.file.calibration.pattern.columns,
                      0:self.config.file.calibration.pattern.rows].T.reshape(-1, 2)
        objp = np.multiply(objp, self.config.file.calibration.pattern.square_size)
        return objp

    def ransac(self, data, model_class, min_samples, threshold, max_trials=100):
        '''
        Fits a model to data with the RANSAC algorithm.
        :param data: numpy.ndarray
            data set to which the model is fitted, must be of shape NxD where
            N is the number of data points and D the dimensionality of the data
        :param model_class: object
            object with the following methods implemented:
             * fit(data): return the computed model
             * residuals(model, data): return residuals for each data point
             * is_degenerate(sample): return boolean value if sample choice is
                degenerate
            see LinearLeastSquares2D class for a sample implementation
        :param min_samples: int
            the minimum number of data points to fit a model
        :param threshold: int or float
            maximum distance for a data point to count as an inlier
        :param max_trials: int, optional
            maximum number of iterations for random sample selection, default 100
        :returns: tuple
            best model returned by model_class.fit, best inlier indices
        '''

        best_model = None
        best_inlier_num = 0
        best_inliers = None
        data_idx = np.arange(data.shape[0])
        for _ in range(max_trials):
            sample = data[np.random.randint(0, data.shape[0], 2)]
            if model_class.is_degenerate(sample):
                continue
            sample_model = model_class.fit(sample)
            sample_model_residua = model_class.residuals(sample_model, data)
            sample_model_inliers = data_idx[sample_model_residua < threshold]
            inlier_num = sample_model_inliers.shape[0]
            if inlier_num > best_inlier_num:
                best_inlier_num = inlier_num
                best_inliers = sample_model_inliers
        if best_inliers is not None:
            best_model = model_class.fit(data[best_inliers])
        return best_model

    def _window_mask(self, image, window_enable=True):

        height, width = image.shape
        window_value = 3
        mask = 0
        if window_enable:
            peak = image.argmax(axis=1)
            _min = peak - window_value
            _max = peak + window_value + 1
            mask = np.zeros_like(image)
            for i in range(height):
                mask[i, _min[i]:_max[i]] = 255
                # Apply mask
        image = cv2.bitwise_and(image, mask)

        return image

    def _threshold_image(self, image, blur_enable=True):

        if self.settings.file.auto_threshold == True:
            threshold_value = 0
            threshold_settings = cv2.THRESH_TOZERO+cv2.THRESH_OTSU
        else:
            threshold_value = self.settings.file.threshold
            threshold_settings = cv2.THRESH_TOZERO


        image = cv2.threshold(
            image, threshold_value, 255, threshold_settings)[1]

        if blur_enable:
            image = cv2.GaussianBlur(image, (7, 7), 0)

        image = cv2.threshold(
            image, threshold_value, 255,  threshold_settings)[1]

        return image

    def _obtain_red_channel(self, image):
        ret = None
        if self.laser_color_channel == 'R (RGB)':
            ret = cv2.split(image)[2]
        elif self.laser_color_channel == 'G (RGB)':
            ret = cv2.split(image)[1]
        elif self.laser_color_channel == 'Cr (YCrCb)':
            ret = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB))[1]
        elif self.laser_color_channel == 'U (YUV)':
            ret = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YUV))[1]

        elif self.laser_color_channel == 'R (HSV)':
            hsv_frame = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            redHueArea = 30
            redRange = ((hsv_frame[:, :, 0] + 360 + redHueArea) % 360)
            hsv_frame[np.where((2 * redHueArea) > redRange)] = [0, 0, 0]
            hsv_frame[np.where(hsv_frame[:, :, 1] < 95)] = [0, 0, 0]
            rgb = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2RGB)
            ret = cv2.split(rgb)[2]

        return ret

    def compute_line_segmentation(self, image, index=0, roi_mask=False):
        if image is not None:
            if roi_mask is True:
                image = self.mask_image(image, index)
            image = self._obtain_red_channel(image)
            if image is not None:
                # Threshold image
                image = self._threshold_image(image)
                # Window mask
                image = self._window_mask(image)

            return image

    def _sgf(self, u, v, s):
        if len(u) > 1:
            i = 0
            sigma = 2.0
            f = np.array([])
            segments = [s[_r] for _r in np.ma.clump_unmasked(np.ma.masked_equal(s, 0))]
            # Detect stripe segments
            for segment in segments:
                j = len(segment)
                # Apply gaussian filter
                fseg = scipy.ndimage.gaussian_filter(u[i:i + j], sigma=sigma)
                f = np.concatenate((f, fseg))
                i += j
            return f, v
        else:
            return u, v

    # RANSAC implementation: https://github.com/ahojnnes/numpy-snippets/blob/master/ransac.py

    def _ransac(self, u, v):
        if len(u) > 1:
            data = np.vstack((v.ravel(), u.ravel())).T
            dr, thetar = self.ransac(data, LinearLeastSquares2D(), 2, 2)
            u = (dr - v * math.sin(thetar)) / math.cos(thetar)
        return u, v

    def compute_2d_points(self, image, index=0, roi_mask=True, preview=False, refinement_method='SGF'):

        if preview:
            _weight_matrix = self._preview_res_weight_matrix
        else:
            _weight_matrix = self._full_res_weight_matrix

        if image is not None:
            image = cv2.GaussianBlur(image, (11,11), 0)
            image = self.compute_line_segmentation(image, index, roi_mask=roi_mask)

            # Peak detection: center of mass
            s = image.sum(axis=1)
            v = np.where(s > 0)[0]
            u = (_weight_matrix * image).sum(axis=1)[v] / s[v]

            if refinement_method == 'SGF':
                # Segmented gaussian filter
                u, v = self._sgf(u, v, s)
            elif refinement_method == 'RANSAC':
                # Random sample consensus
                u, v = self._ransac(u, v)
            return (u, v), image

    def get_texture_stream_frame(self, cam_image):
        cam_image = self.decode_image(cam_image)
        return cam_image

    def get_settings_stream_frame(self, cam_image):
        cam_image = self.decode_image(cam_image)
        return cam_image

    def get_calibration_stream_frame(self, cam_image):
        cam_image = self.decode_image(cam_image)
        gray_image = cv2.cvtColor(cam_image, cv2.COLOR_RGB2GRAY)
        corners = cv2.goodFeaturesToTrack(gray_image, self.config.file.calibration.pattern.columns*self.config.file.calibration.pattern.rows, 0.01, 10)
        corners = np.int0(corners)
        for i in corners:
            x, y = i.ravel()
            cv2.circle(cam_image, (x, y), 3, (0, 0, 255), -1)

        return cam_image

    def get_adjustment_stream_frame(self, cam_image):
        cam_image = self.decode_image(cam_image)
        cv2.resize(cam_image, (self.config.file.camera.preview_resolution.width, self.config.file.camera.preview_resolution.height))
        cv2.line(cam_image, (int(0.5*cam_image.shape[1]),0), (int(0.5*cam_image.shape[1]), cam_image.shape[0]), (0,255,0), thickness=3, lineType=8, shift=0)
        return cam_image

    def drawCorners(self, image):
        corners = self.detect_corners(image)
        cv2.drawChessboardCorners(
            image, (self.config.file.calibration.pattern.columns, self.config.file.calibration.pattern.rows), corners, True)
        return image

    def get_laser_stream_frame(self, image, type='CAMERA'):
        try:

            image = self.decode_image(image, decode=False)

            if bool(self.settings.file.show_laser_overlay):
                points, ret_img = self.compute_2d_points(image, roi_mask=False, preview=True)
                u, v = points
                c = list(zip(u, v))

                for t in c:
                    cv2.line(image, (int(t[0]) - 1, int(t[1])), (int(t[0]) + 1, int(t[1])), (255, 0, 0), thickness=1,
                             lineType=8, shift=0)

            if bool(self.settings.file.show_calibration_pattern):
                cv2.line(image, (int(0.5*image.shape[1]), 0), (int(0.5*image.shape[1]), image.shape[0]), (0, 255, 0), thickness=1, lineType=8, shift=0)
                cv2.line(image, (0, int(0.5*image.shape[0])), (image.shape[1], int(0.5*image.shape[0])), (0, 255, 0), thickness=1, lineType=8, shift=0)
        except Exception as e:
            self._logger.exception(e)

        return image

    def decode_image(self, image, decode=True):
        #if decode:
        #    image = cv2.imdecode(image, 1)
        if self.config.file.camera.rotate == "True":
            image = cv2.transpose(image)
        if self.config.file.camera.hflip == "True":
            image = cv2.flip(image, 1)
        if self.config.file.camera.vflip == "True":
            image = cv2.flip(image, 0)
        return image

    #FIXME: rename color_image into texture_image
    def process_image(self, angle, laser_image, color_image=None, index=0):
        ''' Takes picture and angle (in degrees).  Adds to point cloud '''


        #laser_image = self.decode_image(laser_image)

        try:
            _theta = np.deg2rad(-angle)
            points_2d, image = self.compute_2d_points(laser_image, index)
            # FIXME; points_2d could contain empty arrays, resulting point_cloud to be None
            point_cloud = self.compute_point_cloud(_theta, points_2d, index=index)
            masked_point_cloud = self.mask_point_cloud(point_cloud)

            if color_image is None:

                if index == 1:
                    r, g, b = (255, 0, 0)
                else:
                    r, g, b = self.color

                color_image = np.zeros((self.image_height, self.image_width, 3), np.uint8)
                color_image[:, :, 0] = r
                color_image[:, :, 1] = g
                color_image[:, :, 2] = b

            u, v = points_2d

            texture = color_image[v, np.around(u).astype(int)].T

            return masked_point_cloud, texture
        except Exception as e:
            self._logger.exception("Process Error: {0}".format(e))
            return [], []

    def mask_image(self, image, index):
            if index == 0:
                mask = np.zeros(image.shape, np.uint8)
                mask[0:self.image_height, (self.image_width // 2):self.image_width] = image[0:self.image_height, (self.image_width // 2):self.image_width]
            else:
                mask = np.zeros(image.shape, np.uint8)
                mask[0:self.image_height, 0:(self.image_width // 2)] = image[0:self.image_height, 0:(self.image_width // 2)]

            return mask

    def mask_point_cloud(self, point_cloud):
        if point_cloud is not None and len(point_cloud) > 0:
            rho = np.sqrt(np.square(point_cloud[0, :]) + np.square(point_cloud[1, :]))

            z = point_cloud[2, :]
            turntable_radius = int(self.config.file.turntable.radius)
            idx = np.where(z >= 0 &
                           (z <= 120) &
                           (rho >= -self.config.file.calibration.platform_translation[2]) &
                           (rho <= self.config.file.calibration.platform_translation[2]))[0]


            return point_cloud[:, idx]
        else:
            return point_cloud


    def compute_point_cloud(self, theta, points_2d, index):

        if points_2d[0].size == 0 or points_2d[1].size == 0:
             return None

        # Load calibration values
        R = np.matrix(self.config.file.calibration.platform_rotation)
        t = np.matrix(self.config.file.calibration.platform_translation).T
        # Compute platform transformation
        Xwo = self.compute_platform_point_cloud(points_2d, R, t, index)
        # Rotate to world coordinates
        c, s = np.cos(-theta), np.sin(-theta)
        Rz = np.matrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        Xw = Rz * Xwo
        # Return point cloud
        #if Xw.size > 0:
        #    return np.array(Xw)
        #else:
        #    return None

        return np.array(Xw)

    def compute_platform_point_cloud(self, points_2d, R, t, index):
        # Load calibration values
        n = self.config.file.calibration.laser_planes[index]['normal']
        d = self.config.file.calibration.laser_planes[index]['distance']
        # Camera system
        Xc = self.compute_camera_point_cloud(points_2d, d, n)
        # Compute platform transformation
        return R.T * Xc - R.T * t

    def compute_camera_point_cloud(self, points_2d, d, n):
        # Load calibration values

        fx = self.config.file.calibration.camera_matrix[0][0]
        fy = self.config.file.calibration.camera_matrix[1][1]
        cx = self.config.file.calibration.camera_matrix[0][2]
        cy = self.config.file.calibration.camera_matrix[1][2]

        # Compute projection point
        u, v = points_2d
        x = np.concatenate(((u - cx) / fx, (v - cy) / fy, np.ones(len(u)))).reshape(3, len(u))

        return d / np.dot(n, x) * x


    def detect_corners(self, image, flags=None, type="chessboard"):
        ret = None
        corners = None
        ids = None
        imsize = None

        if type == "chessboard":
            ret, corners = self._detect_chessboard(image, flags)
        elif type == "charucoboard":
            ret, corners, ids, imsize = self._detect_charucoboard(image)

        return ret, corners, ids, imsize

    def detect_pose(self, image, flags=None):

        _, corners, ids, imsize = self.detect_corners(image, flags=flags, type=self.config.file.calibration.pattern.type )
        if corners is not None:
            ret, rvecs, tvecs = cv2.solvePnP(
                self.object_pattern_points, corners,
                np.array(self.config.file.calibration.camera_matrix), np.array(self.config.file.calibration.distortion_vector))
            if ret:
                return (cv2.Rodrigues(rvecs)[0], tvecs, corners)

    def detect_pattern_plane(self, pose):
            if pose is not None:
                R = pose[0]
                t = pose[1].T[0]
                c = pose[2]
                n = R.T[2]
                d = np.dot(n, t)
                return (d, n, c)
            else:
                return None



    def pattern_mask(self, image, corners):
        if image is not None:
            h, w, d = image.shape
            if corners is not None:
                corners = corners.astype(np.int)
                p1 = corners[0][0]
                p2 = corners[self.config.file.calibration.pattern.columns - 1][0]
                p3 = corners[self.config.file.calibration.pattern.columns * (self.config.file.calibration.pattern.rows - 1)][0]
                p4 = corners[self.config.file.calibration.pattern.columns * self.config.file.calibration.pattern.rows - 1][0]
                mask = np.zeros((h, w), np.uint8)
                points = np.array([p1, p2, p4, p3])
                cv2.fillConvexPoly(mask, points, 255)
                image = cv2.bitwise_and(image, image, mask=mask)
        return image

    def _detect_charucoboard(self, image):
        """
        Charuco base pose estimation.
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(gray, self.aruco_dict)

        if len(corners) > 0:
            ret, c_corners, c_ids = cv2.aruco.interpolateCornersCharuco(markerCorners=corners, markerIds=ids, image=gray, board=self.charuco_board, minMarkers=0)
            # ret is the number of detected corners
            if ret > 0:
                imsize = gray.shape
                return ret, c_corners, c_ids, imsize
        else:
            self._logger.debug('Charuco detection Failed!')
            return None, None



    def _detect_chessboard(self, image, flags=None):


        if image is not None:
            if self.config.file.calibration.pattern.rows > 2 and self.config.file.calibration.pattern.columns > 2:

                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

                if flags is None:
                    ret, corners = cv2.findChessboardCorners(gray, (self.config.file.calibration.pattern.columns, self.config.file.calibration.pattern.rows), None)
                else:
                    ret, corners = cv2.findChessboardCorners(gray, (self.config.file.calibration.pattern.columns, self.config.file.calibration.pattern.rows), flags=flags)

                if ret:
                    cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self._criteria)
                    return ret, corners
                else:
                    return None, None