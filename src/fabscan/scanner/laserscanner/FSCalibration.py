import numpy as np
from scipy import optimize
import time
import logging
import struct
from datetime import datetime
from fabscan.util.FSInject import singleton
from fabscan.util.FSUtil import FSSystem
from fabscan.file.FSImage import FSImage
import cv2


from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.FSEvents import FSEventManagerSingleton
from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.scanner.interfaces.FSCalibration import FSCalibrationInterface
from fabscan.FSEvents import FSEventManagerSingleton, FSEvents, FSEvent


# focal_pixel = (focal_mm / sensor_width_mm) * image_width_in_pixels
# And if you know the horizontal field of view, say in degrees,
# focal_pixel = (image_width_in_pixels * 0.5) / tan(FOV * 0.5 * PI/180)


@singleton(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerSingleton,
    imageprocessor=ImageProcessorInterface,
    hardwarecontroller=FSHardwareControllerInterface
)
class FSCalibration(FSCalibrationInterface):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller):
        # super(FSCalibrationInterface, self).__init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller)

        LASER_PLANE_CALIBRATION_START_POS_DEGREE = 65
        LASER_PLANE_CALIBRATION_END_POS_DEGREE = 115
        self._imageprocessor = imageprocessor
        self._hardwarecontroller = hardwarecontroller
        self.config = config
        self.settings = settings
        self._eventmanager = eventmanager.instance

        self.shape = None
        self.camera_matrix = None
        self.distortion_vector = None
        self.image_points = []
        self.object_points = []
        self.calibration_brightness = [20, 20, 20]
        self.quater_turn = int(self.config.turntable.steps / 4)
        self.steps_five_degree = 5.0 / (360.0 / self.config.turntable.steps)
        self.laser_calib_start = LASER_PLANE_CALIBRATION_START_POS_DEGREE * self.steps_five_degree / 5
        self.laser_calib_end = LASER_PLANE_CALIBRATION_END_POS_DEGREE * self.steps_five_degree / 5
        self.total_positions = int(((self.quater_turn/self.steps_five_degree)*4)+2)
        self.current_position = 0
        self._starttime = 0


        self.estimated_t = [-5, 90, 320]

        self._point_cloud = [None, None]
        self.x = []
        self.y = []
        self.z = []
        self._stop = False

        self._logger = logging.getLogger(__name__)

    def reset_calibration_values(self):
        self._point_cloud = [None, None]
        self.x = []
        self.y = []
        self.z = []
        self.current_position = 1
        self.shape = None
        self.camera_matrix = None
        self.distortion_vector = None
        self.image_points = []
        self.object_points = []
        self._starttime = 0

    def start(self):
        tools = FSSystem()
        tools.delete_folder(self.config.folders.scans+'calibration')
        self._hardwarecontroller.turntable.enable_motors()
        self._hardwarecontroller.led.on(self.calibration_brightness[0], self.calibration_brightness[1], self.calibration_brightness[2])
        #self.settings.camera.contrast = 30
        #self.settings.camera.saturation = 20
        #self.settings.camera.brightness = 50
        self.reset_calibration_values()
        self.settings.threshold = 25
        self._starttime = self.get_time_stamp()

        message = {
            "message": "START_CALIBRATION",
            "level": "info"
        }
        self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        self._hardwarecontroller.start_camera_stream(mode="calibration")

        self._do_calibration(self._capture_camera_calibration, self._calculate_camera_calibration)
        self._do_calibration(self._capture_scanner_calibration, self._calculate_scanner_calibration)
        self._hardwarecontroller.led.off()
        self._hardwarecontroller.turntable.disable_motors()

        if self._stop:
            self._logger.debug("Calibration canceled...")
            self._hardwarecontroller.stop_camera_stream()

            # send information to client that calibration is finished
            message = {
                "message": "STOPPED_CALIBRATION",
                "level": "info"
            }
            self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

            self._stop = False
        else:
            self._hardwarecontroller.stop_camera_stream()
            event = FSEvent()
            event.command = 'CALIBRATION_COMPLETE'
            self._eventmanager.publish(FSEvents.COMMAND, event)

            # send information to client that calibration is finished
            message = {
                "message": "FINISHED_CALIBRATION",
                "level": "info"
            }
            self.config.save()

            self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        self.current_position = 0
        self.reset_calibration_values()

    def stop(self):
        self._stop = True


    def _do_calibration(self, _capture, _calibrate):

        # 90 degree turn
        # number of steps for 5 degree turn

        if not self._stop:
            self._hardwarecontroller.turntable.step_blocking(self.quater_turn, speed=900)
#            self._hardwarecontroller.start_camera_stream(mode="calibration")

        position = 0
        while abs(position) < self.quater_turn * 2:

            if not self._stop:

                _capture(position)
                self._hardwarecontroller.turntable.step_interval(-self.steps_five_degree, speed=900)
                position += self.steps_five_degree

                self._logger.debug("Calibration Position "+str(self.current_position)+ " of "+str(self.total_positions))
                message = {
                    "progress": self.current_position,
                    "resolution": self.total_positions,
                    "starttime": self._starttime,
                    "timestamp": self.get_time_stamp()
                }
                self._eventmanager.broadcast_client_message(FSEvents.ON_NEW_PROGRESS, message)
                self.current_position += 1
            else:
                break

        if not self._stop:
            self._hardwarecontroller.turntable.step_blocking(self.quater_turn, speed=900)
            #self._hardwarecontroller.stop_camera_stream()

            _calibrate()



    def _calculate_camera_calibration(self):
        error = 0
        ret, cmat, dvec, rvecs, tvecs = cv2.calibrateCamera(
            self.object_points, self.image_points, self.shape)

        if ret:
            # Compute calibration error
            for i in xrange(len(self.object_points)):
                imgpoints2, _ = cv2.projectPoints(
                    self.object_points[i], rvecs[i], tvecs[i], cmat, dvec)
                error += cv2.norm(self.image_points[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            error /= len(self.object_points)

        self.config.calibration.camera_matrix = np.round(cmat, 3)
        self.config.calibration.distortion_vector = np.round(dvec.ravel(), 3)

        return ret, error, np.round(cmat, 3), np.round(dvec.ravel(), 3), rvecs, tvecs

    def _capture_camera_calibration(self, position):
        image = self._capture_pattern()
        self.shape = image[:, :, 0].shape

        #if (position > self.calib_start and position < self.calib_end):
        #    flags = cv2.CALIB_CB_FAST_CHECK | cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
        #else:
        flags = cv2.CALIB_CB_FAST_CHECK

        corners = self._imageprocessor.detect_corners(image, flags)

        if corners is not None:
            self._logger.debug("Corners detected...")
            if len(self.object_points) < 15:
                self.image_points.append(corners)
                self.object_points.append(self._imageprocessor.object_pattern_points)
                return image


    def _capture_scanner_calibration(self, position):

        image = self._capture_pattern()

        if (position > self.laser_calib_start and position < self.laser_calib_end):
            flags = cv2.CALIB_CB_FAST_CHECK | cv2.CALIB_CB_ADAPTIVE_THRESH #| cv2.CALIB_CB_NORMALIZE_IMAGE
        else:
            flags = cv2.CALIB_CB_FAST_CHECK

        try:
            pose = self._imageprocessor.detect_pose(image, flags)
            plane = self._imageprocessor.detect_pattern_plane(pose)
        except StandardError as e:
            plane = None
            self._logger.error(e)

        if plane is not None:

            distance, normal, corners = plane
            self._logger.debug("Pose detected...  ")
            # Laser triangulation ( Between 60 and 115 degree )
            # angel/(360/3200)
            try:
                #Laser Calibration
                if (position > self.laser_calib_start and position < self.laser_calib_end):
                    #self.settings.camera.contrast = 40
                    #self.settings.camera.brightness = 70
                    self._hardwarecontroller.led.off()
                    for i in xrange(self.config.laser.numbers):
                        image = self._capture_laser(i)
                        image = self._imageprocessor.pattern_mask(image, corners)
                        self.image = image
                        fs_image = FSImage()
                        fs_image.save_image(image, self.current_position, "laser", dir_name="calibration")
                        points_2d, _ = self._imageprocessor.compute_2d_points(image, roi_mask=False, refinement_method='RANSAC')
                        point_3d = self._imageprocessor.compute_camera_point_cloud(
                            points_2d, distance, normal)
                        if self._point_cloud[i] is None:
                            self._point_cloud[i] = point_3d.T
                        else:
                            self._point_cloud[i] = np.concatenate(
                                (self._point_cloud[i], point_3d.T))
                    #self.settings.camera.contrast = 40
                    #self.settings.camera.brightness = 50

                # Platform extrinsics
                origin = corners[self.config.calibration.pattern.columns * (self.config.calibration.pattern.rows - 1)][0]
                origin = np.array([[origin[0]], [origin[1]]])
                t = self._imageprocessor.compute_camera_point_cloud(
                    origin, distance, normal)

            except StandardError, e:
                self._logger.error("Laser Capture Error: "+str(e))
                message = {
                    "message": "LASER_CALIBRATION_ERROR",
                    "level": "error"
                }
                #self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
                t = None

            if t is not None:
                self.x += [t[0][0]]
                self.y += [t[1][0]]
                self.z += [t[2][0]]

            else:
                self.image = image

        self._hardwarecontroller.led.on(self.calibration_brightness[0], self.calibration_brightness[1], self.calibration_brightness[2])

    def _capture_pattern(self):
        #pattern_image = self._hardwarecontroller.get_pattern_image()
        time.sleep(0.5)
        pattern_image = self._hardwarecontroller.get_picture()
        return pattern_image

    def _capture_laser(self, index):
        self._logger.debug("Starting laser capture...")
        time.sleep(1)
        laser_image = self._hardwarecontroller.get_laser_image(index)
        return laser_image

    def _calculate_scanner_calibration(self):
        response = None
        # Laser triangulation
        # Save point clouds
        for i in xrange(self.config.laser.numbers):
            self.save_point_cloud('CALIBRATION_' + str(i) + '.ply', self._point_cloud[i])

        self.distance = [None, None]
        self.normal = [None, None]
        self.std = [None, None]

        # Compute planes
        for i in xrange(self.config.laser.numbers):
            #if self._is_calibrating:
                plane = self.compute_plane(i, self._point_cloud[i])
                self.distance[i], self.normal[i], self.std[i] = plane

        # Platform extrinsics
        self.t = None
        self.x = np.array(self.x)
        self.y = np.array(self.y)
        self.z = np.array(self.z)
        points = zip(self.x, self.y, self.z)

        if len(points) > 4:
            # Fitting a plane
            point, normal = self.fit_plane(points)
            if normal[1] > 0:
                normal = -normal
            # Fitting a circle inside the plane
            center, self.R, circle = self.fit_circle(point, normal, points)
            # Get real origin
            self.t = center - self.config.calibration.pattern.origin_distance * np.array(normal)

            self._logger.info("Platform calibration ")
            self._logger.info(" Center Point: "+str(center))
            self._logger.info(" Translation: " + str(self.t))
            self._logger.info(" Rotation: " + str(self.R).replace('\n', ''))
            self._logger.info(" Normal: " + str(normal))

        # Return response
        result = True
        #self._logger.debug(np.linalg.norm(self.t - self.estimated_t))
        #if self._is_calibrating:
        if self.t is not None and np.linalg.norm(self.t - self.estimated_t) < 180:
            response_platform_extrinsics = (
                self.R, self.t, center, point, normal, [self.x, self.y, self.z], circle)
        else:
            result = False

        response_laser_triangulation = []
        if self.std[0] < 1.0 and self.normal[0] is not None:
            response_laser_triangulation = [{"distance": self.distance[0], "normal":self.normal[0], "deviation":self.std[0]}]
            if self.std[1] < 1.0 and self.normal[1] is not None:
                response_laser_triangulation.append({"distance": self.distance[1], "normal": self.normal[1], "deviation": self.std[1]})
        else:
            result = False

        if result:
            self.config.calibration.platform_translation = self.t
            self.config.calibration.platform_rotation = self.R
            self.config.calibration.laser_planes = response_laser_triangulation
            response = (True, (response_platform_extrinsics, response_laser_triangulation))
        else:
            self._logger.error("Calibration process was not able to estimate laser planes.")
            message = {
                "message": "CALIBRATION_CALCULATION_ERROR",
                "level": "error"
            }
            self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
            response = None

        #self._is_calibrating = False
        self.image = None

        return response

    def compute_plane(self, index, X):
        if X is not None and X.shape[0] > 3:
            model, inliers = self.ransac(X, PlaneDetection(), 3, 0.1)

            distance, normal, M = model
            std = np.dot(M.T, normal).std()

            self._logger.info("Laser calibration " + str(index))
            self._logger.info(" Distance: " + str(distance))
            self._logger.info(" Normal: " + str(normal))
            self._logger.info(" Standard deviation: " + str(std))
            self._logger.info(" Point cloud size: " + str(len(inliers)))

            return distance, normal, std
        else:
            return None, None, None

    def distance2plane(self, p0, n0, p):
        return np.dot(np.array(n0), np.array(p) - np.array(p0))

    def residuals_plane(self, parameters, data_point):
        px, py, pz, theta, phi = parameters
        nx, ny, nz = np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)
        distances = [self.distance2plane(
            [px, py, pz], [nx, ny, nz], [x, y, z]) for x, y, z in data_point]
        return distances

    def fit_plane(self, data):
        estimate = [0, 0, 0, 0, 0]  # px,py,pz and zeta, phi
        # you may automize this by using the center of mass data
        # note that the normal vector is given in polar coordinates
        best_fit_values, ier = optimize.leastsq(self.residuals_plane, estimate, args=(data))
        xF, yF, zF, tF, pF = best_fit_values

        # point  = [xF,yF,zF]
        point = data[0]
        normal = -np.array([np.sin(tF) * np.cos(pF), np.sin(tF) * np.sin(pF), np.cos(tF)])

        return point, normal

    def residuals_circle(self, parameters, points, s, r, point):
        r_, s_, Ri = parameters
        plane_point = s_ * s + r_ * r + np.array(point)
        distance = [np.linalg.norm(plane_point - np.array([x, y, z])) for x, y, z in points]
        res = [(Ri - dist) for dist in distance]
        return res

    def fit_circle(self, point, normal, points):
        # creating two inplane vectors
        # assuming that normal not parallel x!
        s = np.cross(np.array([1, 0, 0]), np.array(normal))
        s = s / np.linalg.norm(s)
        r = np.cross(np.array(normal), s)
        r = r / np.linalg.norm(r)  # should be normalized already, but anyhow

        # Define rotation
        R = np.array([s, r, normal]).T

        estimate_circle = [0, 0, 0]  # px,py,pz and zeta, phi
        best_circle_fit_values, ier = optimize.leastsq(
            self.residuals_circle, estimate_circle, args=(points, s, r, point))

        rF, sF, RiF = best_circle_fit_values

        # Synthetic Data
        center_point = sF * s + rF * r + np.array(point)
        synthetic = [list(center_point + RiF * np.cos(phi) * r + RiF * np.sin(phi) * s)
                     for phi in np.linspace(0, 2 * np.pi, 50)]
        [cxTupel, cyTupel, czTupel] = [x for x in zip(*synthetic)]

        return center_point, R, [cxTupel, cyTupel, czTupel]

    def ransac(self, data, model_class, min_samples, threshold, max_trials=500):
        best_model = None
        best_inlier_num = 0
        best_inliers = None
        data_idx = np.arange(data.shape[0])
        for _ in xrange(max_trials):
            sample = data[np.random.randint(0, data.shape[0], 3)]
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
        return best_model, best_inliers


    def save_point_cloud(self, filename, point_cloud):
        if point_cloud is not None:
            f = open(self.config.folders.scans+'/calibration/'+filename, 'wb')
            self.save_point_cloud_stream(f, point_cloud)
            f.close()

    def save_point_cloud_stream(self, stream, point_cloud):
        frame = "ply\n"
        frame += "format binary_little_endian 1.0\n"
        frame += "comment Generated by FabScanPi software\n"
        frame += "element vertex {0}\n".format(len(point_cloud))
        frame += "property float x\n"
        frame += "property float y\n"
        frame += "property float z\n"
        frame += "property uchar red\n"
        frame += "property uchar green\n"
        frame += "property uchar blue\n"
        frame += "element face 0\n"
        frame += "property list uchar int vertex_indices\n"
        frame += "end_header\n"
        for point in point_cloud:
            frame += struct.pack("<fffBBB", point[0], point[1], point[2], 255, 0, 0)
        stream.write(frame)

    def get_time_stamp(self):
        return int(datetime.now().strftime("%s%f"))/1000

import numpy.linalg


# from scipy.sparse import linalg


class PlaneDetection(object):
    def fit(self, X):
        M, Xm = self._compute_m(X)
        # U = linalg.svds(M, k=2)[0]
        # normal = np.cross(U.T[0], U.T[1])
        normal = numpy.linalg.svd(M)[0][:, 2]
        if normal[2] < 0:
            normal *= -1
        dist = np.dot(normal, Xm)
        return dist, normal, M

    def residuals(self, model, X):
        _, normal, _ = model
        M, Xm = self._compute_m(X)
        return np.abs(np.dot(M.T, normal))

    def is_degenerate(self, sample):
        return False

    def _compute_m(self, X):
        n = X.shape[0]
        Xm = X.sum(axis=0) / n
        M = np.array(X - Xm).T
        return M, Xm
