__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import math
import logging, os
import numpy as np
import scipy.ndimage
import cv2
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.util.FSInject import inject
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

class FSPoint():
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

class FSLine():
    def __init__(self, a=0.0, b=0.0):
        self.a = float(a)
        self.b = float(b)


@inject(
    config=ConfigInterface,
    settings=SettingsInterface
)
class ImageProcessor(ImageProcessorInterface):
    def __init__(self, config, settings):

        self.settings = settings
        self.config = config
        self._logger = logging.getLogger(__name__)
        self.red_channel = 'R (RGB)'
        self.threshold_enable = False
        self.threshold_value = 0
        self.blur_enable = False
        self.blur_value = 0
        self.window_enable = False
        self.window_value = 0
        self.refinement_method = ''
        self.image_height = self.config.camera.resolution.height
        self.image_width = self.config.camera.resolution.width
        self._weight_matrix = self.config.weight_matrix

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
        for _ in xrange(max_trials):
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

        window_value = 3
        mask = 0
        if window_enable:
            peak = image.argmax(axis=1)
            _min = peak - window_value
            _max = peak + window_value + 1
            mask = np.zeros_like(image)
            for i in xrange(self.image_height):
                mask[i, _min[i]:_max[i]] = 255
                # Apply mask
        image = cv2.bitwise_and(image, mask)

        return image

    def _threshold_image(self, image, blur_enable=True):
        # if self.threshold_enable:

        image = cv2.threshold(
            image, 10, 255, cv2.THRESH_TOZERO)[1]

        if blur_enable:
            image = cv2.blur(image, (5, 5))

        image = cv2.threshold(
            image, 10, 255, cv2.THRESH_TOZERO)[1]

        return image

    def _obtain_red_channel(self, image):
        ret = None
        # if self.red_channel == 'R (RGB)':
        ret = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # ret = cv2.split(image)[0]

        # elif self.red_channel == 'Cr (YCrCb)':
        # ret = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YCR_CB))[1]
        # elif self.red_channel == 'U (YUV)':
        # ret = cv2.split(cv2.cvtColor(image, cv2.COLOR_RGB2YUV))[1]
        return ret


    def compute_line_segmentation(self, image, roi_mask=False):
        if image is not None:
            # Apply ROI mask
            # if roi_mask:
            #   image = self.point_cloud_roi.mask_image(image)
            # Obtain red channel

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


    def compute_2d_points(self, image, refinement_method='SGF'):
        if image is not None:

            image = self.compute_line_segmentation(image)
            # Peak detection: center of mass

            s = image.sum(axis=1)
            v = np.where(s > 0)[0]
            u = (self._weight_matrix * image).sum(axis=1)[v] / s[v]

            if refinement_method == 'SGF':
                # Segmented gaussian filter
                u, v = self._sgf(u, v, s)
            elif refinement_method == 'RANSAC':
                # Random sample consensus
                u, v = self._ransac(u, v)
            return (u, v), image


    #### END NEW CODE

    def get_texture_stream_frame(self,cam_image):
        return cam_image

    def get_calibration_stream_frame(self,cam_image):


        cv2.line(cam_image, (0,int(self.config.scanner.origin.y*cam_image.shape[0])), (cam_image.shape[1],int(self.config.scanner.origin.y*cam_image.shape[0])), (0,255,0), thickness=1, lineType=8, shift=0)
        cv2.line(cam_image, (int(0.5*cam_image.shape[1]),0), (int(0.5*cam_image.shape[1]), cam_image.shape[0]), (0,255,0), thickness=1, lineType=8, shift=0)
        cv2.line(cam_image, (0,int(cam_image.shape[0]*self.config.laser.detection_limit)), (int(cam_image.shape[1]), int(cam_image.shape[0]*self.config.laser.detection_limit)), (0,0,255), thickness=1, lineType=8, shift=0)
        r = 320.0 / cam_image.shape[1]
        dim = (320, int(cam_image.shape[0] * r))
        cam_image = cv2.resize(cam_image, dim, interpolation = cv2.INTER_AREA)
        return cam_image


    def get_laser_stream_frame(self, image, type='CAMERA'):


        points, ret_img = self.compute_2d_points(image)
        u, v = points
        c = zip(u, v)

        for t in c:
            cv2.line(image, (int(t[0]) - 4, int(t[1])), (int(t[0]) + 4, int(t[1])), (255, 0, 0), thickness=1,
                     lineType=8, shift=0)

        r = 800.0 / image.shape[1]
        dim = (800, int(image.shape[0] * r))
        image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)

        return image


    def process_image(self, angle, laser_image, color_image=None):
        ''' Takes picture and angle (in degrees).  Adds to point cloud '''

        x_center = laser_image.shape[1] * self.settings.center
        x_center_delta = laser_image.shape[1] * 0.5 - x_center

        pixels, image = self.line_coords(laser_image, filter=True, fast=False, x_center_delta=x_center_delta)  # Get line coords from image

        points = self.process_line(pixels, angle, color_image)
        return points


    def calculate_laser_angle(self, calibration_image):


        point = self.detect_laser(calibration_image)

        if point != None:
            self._logger.debug("Found a point for laser angle calculation")
            self.settings.backwall.laser.x = point.x
            self.settings.backwall.laser.y = point.y
            self.settings.backwall.laser.z = point.z

            b = self.config.laser.position.x - point.x
            a = self.config.laser.position.z - point.z
            angle = math.atan(b/a) * 180.0 / math.pi
            self.settings.backwall.laser_angle = angle
            return angle
        else:
            self._logger.debug("No laser angle calculated")
            return None



    def detect_laser(self, image):

        x_center = image.shape[1] * self.settings.center
        x_center_delta = image.shape[1] * 0.5 - x_center

        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        dir_name = basedir+"/static/"
        cv2.imwrite(dir_name+"debug.jpg", image)

        x, image = self.line_coords(image, filter=False, fast=True, x_center_delta=x_center_delta)

        try:
            if x != []:
                x = x[:,0]
                new_x = []

                self._logger.debug(image.shape[0]*self.config.laser.detection_limit)
                detection_pixel_start_limit = int(image.shape[0]*self.config.laser.detection_limit)
                for i in xrange(detection_pixel_start_limit, detection_pixel_start_limit+20):
                    new_x.append(x[i])


                x = np.sort(new_x)
                point = FSPoint( x[len(x)/2] , 0.0, 0.0)

                # save pixel position of laser line x direction
                self.settings.backwall.laser_pixel_position = point.x

                # make a camera system point of laser line on backwall
                laser_backwall = FSPoint()
                laser_backwall.x = point.x
                laser_backwall = self.convertCvPointToPoint(laser_backwall)


                self.settings.backwall.laser.x = laser_backwall.x
                self.settings.backwall.laser.y = laser_backwall.y
                self.settings.backwall.laser.z = laser_backwall.z

                self._logger.debug("Laser on backwall detected at x-pixel position: %d" % (point.x, ))

                fs_point = self.convertCvPointToPoint(point)

                return fs_point

            else:
                self._logger.debug("Can not detect laser line on backwall.")
                return None

        except:
                self._logger.debug("Can not detect laser line on backwall.")
                return None

    def get_grey(self, image):
        hsv_img = cv2.cvtColor(image, cv2.cv.CV_BGR2HSV)
        h, s, v = cv2.split(hsv_img)
        height, width, channels = image.shape

        blur = cv2.GaussianBlur(v,(11,11),0)
        return blur

    def trheshold_image(self, image):
        #hsv_img = cv2.cvtColor(image, cv2.cv.CV_BGR2HSV)
        #h, s, v = cv2.split(hsv_img)
        #height, width, channels = image.shape

        red_channel = image
        red_channel[2,2,:] = 0
        open_value = 2
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (open_value, open_value))
        image_open = cv2.morphologyEx(red_channel, cv2.MORPH_OPEN, kernel)
        image_threshold =cv2.threshold(image_open, self.settings.threshold, self.settings.threshold+20,  cv2.THRESH_TOZERO)[1]

        gray_image = cv2.cvtColor(image_threshold, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.GaussianBlur(gray_image,(5,5),0)

        return gray_image



    def line_coords(self, image,  filter=True, fast=False, x_center_delta=None):
        '''
        Return [a list of (x,y)] tuples representing middle white pixel per line
        If x_center given, transforms coordinates so that
            the axis of rotation is x=0.
        '''
        #grey = self.trheshold_image(image)
        #self._logger.debug("Laser Position Value "+ str(self.config.laser.position.x))
        h, w, c = image.shape
        grey = self.get_grey(image)

        #camera_matrix = np.matrix(self.config.calibration.camera_matrix)
        #dist_coefficients = np.matrix(self.config.calibration.dist_coefficients)
        #newcamera, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefficients, (w, h), 0)
        #grey = cv2.undistort(grey, camera_matrix, dist_coefficients, newcamera, None)

        threshold = cv2.cvtColor(grey, cv2.COLOR_GRAY2BGR)

        pixels = []
        if filter:
            start = self.settings.backwall.laser_pixel_position+20
        else:
            start = 0

        if fast:

            for y, line in enumerate(grey):
                    sub_pixel = np.argmax(line[ start: grey.shape[1]]) + start

                    if line[sub_pixel] > self.settings.threshold/3:
                        cv2.line(threshold, (int(sub_pixel)-5, int(y)), (int(sub_pixel)+5, int(y)), (255, 0, 0), thickness=1, lineType=8, shift=0)
                        pixels.append((sub_pixel, y))

        else:

            # TODO: handle multiple points in one line
            start = self.settings.backwall.laser_pixel_position+60
            id = np.indices((image.shape[0], image.shape[1]))[1]

            grey[grey < self.settings.threshold/3] = 0

            id_mul = id[:, start:]*grey[:, start:]

            sum_t = id_mul.astype(float).sum(axis=1)
            sum_a = grey[:, start:].astype(float).sum(axis=1)

            weight = np.squeeze(sum_t/sum_a)

            it = np.nditer(weight, flags=['f_index'])
            while not it.finished:

                   if it[0] > 0:
                       pixels.append((float(it[0]),it.index))
                       cv2.line(threshold, (int(it[0])-5, int(it.index)), (int(it[0])+5, int(it.index)), (255, 0, 0), thickness=1, lineType=8, shift=0)

                   it.iternext()



        if x_center_delta:
               pixels = [(x -x_center_delta, y) for (x, y) in pixels]


        return np.array(pixels), threshold


    def process_line(self, line_coords, angle, color_image=None):


        point_line = []

        for x, y in line_coords:

            try:
                self._logger.debug("u: {}, v: {}".format(x, y))
                # create new cv point
                #x_center = self.config.camera.resolution.width * self.settings.center
                # laser_point = FSPoint(x+x_center ,y)

                #point = FSPoint(, )

                #TODO: make config params a global param in image processor
                camera_matrix = np.matrix(self.config.calibration.camera_matrix)
                fx = camera_matrix.item((0, 0))
                fy = camera_matrix.item((1, 1))
                cx = camera_matrix.item((0, 2))
                cy = camera_matrix.item((1, 2))

                #self._logger.debug("fx: {}, fy: {}, cx: {}, cy: {}".format(fx, fy, cx, cy))

                #fx = camera_matrix[0][0]
                #fy = camera_matrix[1][1]
                #cx = camera_matrix[0][2]
                #cy = camera_matrix[1][2]

                d = float(self.config.calibration.plane.distance)
                n = np.matrix(self.config.calibration.plane.normal).T
                t = np.matrix(self.config.calibration.plane.translation).T
                R = np.matrix(self.config.calibration.plane.rotation)

                x = np.matrix([[(float(x) - cx) / fx], [(float(y) - cy) / fy], [1]])

                x_c = (d / float(n.T.dot(x))) * x
                #self._logger.debug("X_c"+str(x_c))

                x_wo = R.T * x_c - R.T * t

                theta = np.deg2rad(angle)

                #theta = angle * np.pi / 180.0
                c = np.cos(theta)
                s = np.sin(theta)
                R_z = np.matrix([[c, -s, 0], [s, c, 0], [0, 0, 1]])

                x_w = R_z * x_c

                #self._logger.debug(x_w)
                new_point = dict()
                new_point['x'] = str(round(x_w.item(0), 2))
                new_point['y'] = str(round(x_w.item(1), 2))
                new_point['z'] = str(round(x_w.item(2), 2))
                new_point['r'] = str(0)
                new_point['g'] = str(0)
                new_point['b'] = str(0)

                point_line.append(new_point)
                #self._logger.debug(new_point)

                #point_line.append(new_point)

                # ## world coordinates without deepth
                # point = self.convertCvPointToPoint(point)
                #
                # camera_position = FSPoint(float(self.config.camera.position.x), float(self.config.camera.position.y), float(self.config.camera.position.z))
                # laser_position = FSPoint(float(self.config.laser.position.x),float(self.config.laser.position.y),float(self.config.laser.position.z))
                # laser_backwall = FSPoint(float(self.settings.backwall.laser.x),float(self.settings.backwall.laser.y), float(self.settings.backwall.laser.z))
                #
                #
                # line1 = self.computeLineFromPoints(camera_position, point)
                # line2 = self.computeLineFromPoints(laser_backwall, laser_position)
                #
                # if not (line1 is None or line2 is None):
                #
                #     intersection = self.computeLineIntersections(line1, line2)
                #
                #     point.x = intersection.x
                #     point.z = intersection.z
                #
                #     point.y -= float(self.config.camera.position.y)
                #     point.y *= (float(self.config.camera.position.z) - point.z)/float(self.config.camera.position.z)
                #     point.y += float(self.config.camera.position.y)
                #
                #     point.z -= float(self.config.turntable.position.z)
                #     alphaDetla = angle
                #     alphaOld = float(math.atan(point.z/point.x))
                #     alphaNew = float(alphaOld+alphaDetla*(math.pi/180.0))
                #     hypotenuse = float(math.sqrt(point.x*point.x + point.z*point.z))
                #
                #     if point.z < 0 and point.x < 0:
                #         alphaNew += math.pi
                #     elif (point.z > 0) and (point.x < 0):
                #         alphaNew -= math.pi
                #
                #     point.z = math.sin(alphaNew)*hypotenuse
                #     point.x = math.cos(alphaNew)*hypotenuse
                #
                #     lowerLimit = 1.09
                #     topLimit = self.config.camera.resolution.height - self.config.camera.resolution.height*self.config.scanner.origin.y
                #
                #     if y > topLimit:
                #         if (point.y > lowerLimit and hypotenuse < 7 ):
                #             new_point = dict()
                #
                #             new_point['x'] = str(point.x)
                #             new_point['y'] = str(point.y)
                #             new_point['z'] = str(-point.z)
                #
                #             if not color_image is None:
                #                 b,g,r = color_image[y,x]
                #                 new_point['r'] = str(r)
                #                 new_point['g'] = str(g)
                #                 new_point['b'] = str(b)
                #
                #
                #             point_line.append(new_point)
            except Exception as e:
                self._logger.error(e)
                self._logger.error("Value Calculation Error occured.")


        return point_line


    def computeLineFromPoints(self, p1, p2):
        try:
            line = FSLine()
            line.a = (p2.z-p1.z)/(p2.x-p1.x)
            line.b = p1.z-line.a*p1.x
            return line
        except:
            return None

    def computeLineIntersections(self,  line1, line2):
        intersection = FSPoint()
        intersection.x = (line2.b - line1.b)/(line1.a-line2.a)
        intersection.z = line2.a*intersection.x+line2.b
        return intersection


    def convertPointToCvPoint(self, point):
        fsImgWidth = self.config.camera.frame.dimension
        fsImgHeight = self.config.camer.frame.dimension*(self.config.camera.resolution.height/self.config.camera.resolution.width)

        origin = FSPoint(self.config.camera.resolution.width/2.0, self.config.camera.resolution.height*self.config.scanner.origin.y)
        point_x = (point.x*self.config.camera.resolution.width/fsImgWidth) + origin.x
        point_y = (-point.y*self.config.camera.resolution.height/fsImgHeight) +origin.y

        cvPoint = FSPoint(point_x, point_y)
        return cvPoint


    def convertCvPointToPoint(self, cvPoint):

        fsImgWidth = self.config.camera.frame.dimension
        fsImgHeight = fsImgWidth*(float(self.config.camera.resolution.height)/ float(self.config.camera.resolution.width))
        origin = FSPoint(self.config.camera.resolution.width/2.0, float(self.config.camera.resolution.height)*self.config.scanner.origin.y)
        point = FSPoint()
        point.x = (cvPoint.x -origin.x)*fsImgWidth/float(self.config.camera.resolution.width)
        point.y = -(cvPoint.y - origin.y)*fsImgHeight/float(self.config.camera.resolution.height)
        point.z = 0.0

        return point



