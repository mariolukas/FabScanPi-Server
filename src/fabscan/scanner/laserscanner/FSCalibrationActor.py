import numpy as np
from scipy import optimize
import time
import logging
import struct
from datetime import datetime
import cv2
import sys
import copy
import math

from fabscan.lib.util.FSInject import singleton
from fabscan.lib.util.FSUtil import FSSystem
from fabscan.lib.file.FSImage import FSImage
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.scanner.interfaces.FSCalibrationActor import FSCalibrationActorInterface, FSCalibrationMode
from fabscan.FSEvents import FSEventManagerSingleton, FSEvents, FSEvent

@singleton(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerSingleton,
    imageprocessor=ImageProcessorInterface,
    hardwarecontroller=FSHardwareControllerInterface
)
class FSCalibrationActor(FSCalibrationActorInterface):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller):
        super(FSCalibrationActorInterface, self).__init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller)

        self.LASER_PLANE_CALIBRATION_START_POS_DEGREE = 30 #15 #20 #25 #30 #65
        self.LASER_PLANE_CALIBRATION_END_POS_DEGREE = 150 #165 #160 #155 #150 #115
        self._imageprocessor = imageprocessor
        self._hardwarecontroller = hardwarecontroller
        self.config = config
        self.settings = settings
        self._eventmanager = eventmanager.instance

        self.current_calibration_step = 0
        self.shape = None
        self.camera_matrix = None
        self.distortion_vector = None

        self.image_points = []
        self.object_points = []
        self.aruco_ids = []

        self.calibration_brightness = [100, 100, 100]
        self.quater_turn = int(self.config.file.turntable.steps / 4)

        self.motor_move_degree = 3.6 # 1.8,  2.7 , 3.6, 5.0
        self.steps_five_degree = int(self.motor_move_degree / (360 / self.config.file.turntable.steps))
        self.laser_calib_start = self.LASER_PLANE_CALIBRATION_START_POS_DEGREE * self.steps_five_degree / 5
        self.laser_calib_end = self.LASER_PLANE_CALIBRATION_END_POS_DEGREE * self.steps_five_degree / 5

        self.motorsteps_per_calibration_step = int(self.motor_move_degree / (360 / self.config.file.turntable.steps))
        self.total_positions = int(((self.quater_turn / self.motorsteps_per_calibration_step) * 4) + 2)
        self.current_position = 0
        self._starttime = 0
        self.position = 0
        self._stop_calibration = False
        self.current_calibtation_mode = "IDLE"

        self.finish_camera_calibration = False
        self.estimated_t = [-5, 90, 320]

        self.raw_image_count = 0
        self._point_cloud = [None, None]
        self.x = []
        self.y = []
        self.z = []

        #self._stop_calibration = False
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Calibration Actor initilaizeed")


    def on_stop(self):
        self._logger.debug("Calibration Actor stopped.")

    def on_receive(self, event):
        if event[FSEvents.COMMAND] == "START_CALIBRATION":
            self._logger.debug("Calibration Mode: {0}".format(event['mode']))

            if (event['mode'] == FSCalibrationMode.MODE_AUTO_CALIBRATION):
                self.reset_calibration_values()
                self.start_hardware_components()

            self.current_calibtation_mode = event['mode']

            if self.current_calibtation_mode:
                self.on_calbration_start()
            else:
                message = {
                    "message": "CALIBRATION_MODE_NOT_DEFINED",
                    "level": "error"
                }
                self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
                event = FSEvent()

                event.command = 'STOP'
                self._eventmanager.publish(FSEvents.COMMAND, event)

        if event[FSEvents.COMMAND] == "STOP_CALIBRATION":
            self.on_calibtation_stop()
            self._logger.debug("Stopping Calibration")

        if event[FSEvents.COMMAND] == "TRIGGER_MANUAL_CAMERA_CALIBRATION_STEP":
            self.current_calibration_step += 1
            self.on_manual_calibration_trigger()

        if event[FSEvents.COMMAND] == "TRIGGER_AUTO_LASER_CALIBRATION_STEP":
            self.on_auto_calibration_trigger(self._capture_scanner_calibration, self._calculate_scanner_calibration)

        if event[FSEvents.COMMAND] == "TRIGGER_AUTO_CAMERA_CALIBRATION_STEP":
            self.on_auto_calibration_trigger(self._capture_camera_calibration, self._calculate_camera_calibration)

        if event[FSEvents.COMMAND] == "FINISH_MANUAL_CAMERA_CALIBRATION":
            self.finish_camera_calibration = True
            self.on_manual_calibration_trigger()

        if event[FSEvents.COMMAND] == "CALIBRATION_COMPLETE":
            self.raw_image_count = 0
            self.on_calbration_complete()

    def reset_calibration_values(self):
        self.current_calibtation_mode = "IDLE"
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
        self.aruco_ids = []
        self._starttime = 0
        self.current_calibration_step = 0
        self._stop_calibration = False
        self.finish_camera_calibration = False
        self.position = 0
        self._hardwarecontroller.reset_devices()


    def on_calbration_start(self):

        tools = FSSystem()
        self._logger.debug("Camera Calibration in {0} Mode started".format(self.current_calibtation_mode))
        tools.delete_folder(self.config.file.folders.scans+'calibration')
        self.current_calibration_step = 0
        self.settings.threshold = 25
        self._starttime = self.get_time_stamp()

        message = {
            "message": "START_CALIBRATION",
            "level": "info"
        }
        self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        try:

            if (self.current_calibtation_mode == FSCalibrationMode.MODE_AUTO_CALIBRATION):
                self.on_auto_calibration_trigger(self._capture_camera_calibration, self._calculate_camera_calibration)

            if (self.current_calibtation_mode == FSCalibrationMode.MODE_SCANNER_CALIBRATION):
                self.position = 0
                self.on_auto_calibration_trigger(self._capture_scanner_calibration, self._calculate_scanner_calibration)

        except Exception as e:
             self._logger.exception(e)
             message = {
                     "message": "SCANNER_CALIBRATION_FAILED",
                     "level": "warn"
             }
             self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def start_hardware_components(self):
        self._hardwarecontroller.turntable.enable_motors()

        #if self.config.file.laser.interleaved == "False":
        self._logger.debug("Turning Leds on in non interleaved mode.")
        self._hardwarecontroller.led.on(self.calibration_brightness[0], self.calibration_brightness[1], self.calibration_brightness[2])

        #self._hardwarecontroller.start_camera_stream(mode="calibration")

    def stop_hardware_components(self):
        self._hardwarecontroller.reset_devices()

    def on_calibtation_stop(self):
        self.stop_hardware_components()
        self._logger.debug("Calibration canceled...")
        self._stop_calibration = True
        # send information to client that calibration is finished
        message = {
            "message": "STOPPED_CALIBRATION",
            "level": "info"
        }
        self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def on_calbration_complete(self):
        #self.stop_hardware_components()
        event = FSEvent()

        event.command = 'CALIBRATION_COMPLETE'
        self._eventmanager.publish(FSEvents.COMMAND, event)
        self._logger.debug("Calibration finished.")

        # send information to client that calibration is finished
        message = {
                "message": "FINISHED_CALIBRATION",
                "level": "info"
        }
        self.config.save_json()

        if self.config.file.laser.interleaved == "False":
            self._hardwarecontroller.led.off()

        self._hardwarecontroller.turntable.disable_motors()

        self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.reset_calibration_values()

    def on_manual_calibration_trigger(self):

        if not self.finish_camera_calibration and not self._stop_calibration:
            self._logger.debug("Manual Calibration triggered...")
            self._capture_camera_calibration(self.current_calibration_step)

        if self.finish_camera_calibration:
            self._calculate_camera_calibration()
            self.finish_camera_calibration = False
            self.actor_ref.tell({FSEvents.COMMAND: "CALIBRATION_COMPLETE"})


    def on_auto_calibration_trigger(self, _capture, _calibrate):

        # 90 degree turn
        try:
            # the calibration was stopped or just started.
            if not self._stop_calibration and self.position == 0:
                self._hardwarecontroller.move_to_next_position(steps=self.quater_turn, speed=5000)
                time.sleep(3)

            if abs(self.position) < self.quater_turn * 2:
                self._logger.debug("Step {0} of {1} in {2}.".format(self.current_position, self.total_positions, self.current_calibtation_mode))

                if not self._stop_calibration:

                    _capture(self.position)

                    self._hardwarecontroller.move_to_next_position(steps=-self.motorsteps_per_calibration_step, speed=1000)
                    self.position += self.motorsteps_per_calibration_step

                    message = {
                        "progress": self.current_position,
                        "resolution": self.total_positions,
                        "starttime": self._starttime,
                        "timestamp": self.get_time_stamp()
                    }
                    self._eventmanager.broadcast_client_message(FSEvents.ON_NEW_PROGRESS, message)
                    self.current_position += 1

            # the calibration is done, go over to the next calibration step or just exit.
            if not self._stop_calibration and abs(self.position) == self.quater_turn * 2:
                self._hardwarecontroller.move_to_next_position(steps=self.quater_turn, speed=5000)
                _calibrate()
                #  if mode is auto calibration, we just finished the auto camera calibration, now move over to
                #  scanner calibration, if we are not in auto calibration mode (anymore) we are done with the calibration
                if ( self.current_calibtation_mode == FSCalibrationMode.MODE_AUTO_CAMERA_CALIBRATION or
                     self.current_calibtation_mode == FSCalibrationMode.MODE_AUTO_CALIBRATION):
                    self.actor_ref.tell({FSEvents.COMMAND: "START_CALIBRATION", 'mode': FSCalibrationMode.MODE_SCANNER_CALIBRATION})
                else:
                    self.actor_ref.tell({FSEvents.COMMAND: "CALIBRATION_COMPLETE"})

            # we are not done here, trigger the actor itself for the next step
            if abs(self.position) < self.quater_turn * 2 and not self._stop_calibration:
                # we are still in auto camera calibraion mode.
                if ( self.current_calibtation_mode == FSCalibrationMode.MODE_AUTO_CALIBRATION ):
                    self.actor_ref.tell({FSEvents.COMMAND: "TRIGGER_AUTO_CAMERA_CALIBRATION_STEP"})

                # we are still in laser calibration mode.
                if (self.current_calibtation_mode == FSCalibrationMode.MODE_SCANNER_CALIBRATION):
                    self.actor_ref.tell({FSEvents.COMMAND: "TRIGGER_AUTO_LASER_CALIBRATION_STEP"})

        except Exception as e:
            self._logger.exception("Calibration Error: {0}".format(e))


    def _calculate_camera_calibration(self):
        error = 0
        try:
            if len(self.object_points) == 0 or len(self.image_points) == 0:
                raise Exception('Calibration Failed')

            if self.config.file.calibration.pattern.type == "chessboard":
                try:
                    ret, cmat, dvec, rvecs, tvecs = cv2.calibrateCamera(self.object_points, self.image_points, self.shape, None, None)
                except Exception as e:
                    self._logger.error(e)

            elif self.config.file.calibration.pattern.type == "charucoboard":
                ret, cmat, dvec, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
                    charucoCorners=self.image_points,
                    charucoIds=self.aruco_ids,
                    board=self._imageprocessor.get_aruco_board(),
                    imageSize=self.shape,
                    cameraMatrix=None,
                    distCoeffs=None
                )

            else:
                raise Exception('Calibration Failed: Unknown Calibration Pattern Type in Config.')

            self._logger.debug("Rep Error: {0}".format(ret))

            if ret:
                # Compute calibration error
                if self.config.file.calibration.pattern.type == "chessboard":
                    for i in range(len(self.object_points)):
                        imgpoints2, _ = cv2.projectPoints(
                            self.object_points[i],
                            rvecs[i],
                            tvecs[i],
                            cmat,
                            dvec
                        )
                        error += cv2.norm(
                            self.image_points[i],
                            imgpoints2,
                            cv2.NORM_L2
                        ) / len(imgpoints2)

                    error /= len(self.object_points)


                self.config.file.calibration.camera_matrix = copy.deepcopy(np.round(cmat, 3))
                self.config.file.calibration.distortion_vector = copy.deepcopy(np.round(dvec.ravel(), 3))

                self._logger.debug("Camera Matrix {0}".format(np.round(cmat, 3)))
                self._logger.debug("Distortion Vector {0}".format(np.round(dvec.ravel(), 3)))
                self._logger.debug("Total Error {0}".format(error))
            return ret, error, np.round(cmat, 3), np.round(dvec.ravel(), 3), rvecs, tvecs
        except Exception as e:
            self._logger.error("Error while laser calibration calculations: {0}".format(e))

        return ret, error, np.round(cmat, 3), np.round(dvec.ravel(), 3), rvecs, tvecs

    def _capture_camera_calibration(self, position):
        image = self._capture_pattern()
        self.shape = image[:, :, 0].shape

        if bool(self.config.file.keep_calibration_raw_images):
            fs_image = FSImage()
            fs_image.save_image(image, self.raw_image_count, "calibration", dir_name="calib_test")
            self.raw_image_count += 1

            #TODO: find out if it is better and try this...again.
        if (position > self.laser_calib_start and position < self.laser_calib_end):
           flags = cv2.CALIB_CB_FAST_CHECK | cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
        else:
           flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK

        _, corners, ids, _ = self._imageprocessor.detect_corners(image, flags, type=self.config.file.calibration.pattern.type)

        if corners is not None:
            self._logger.debug("Corners detected...")
            if len(self.object_points) < 15:
                self._logger.debug("Appending new points ...")
                self.image_points.append(corners)
                self.object_points.append(self._imageprocessor.object_pattern_points)

                if ids is not None:
                    self._logger.debug("Appending new charuco ids ...")
                    self.aruco_ids.append(ids)

                return image

        else:
            self._logger.debug("No corners detected moving on.")

    def _capture_scanner_calibration(self, position):

        pattern_image = self._capture_pattern()

        if bool(self.config.file.keep_calibration_raw_images):
            fs_image = FSImage()
            fs_image.save_image(pattern_image, self.raw_image_count, "calibration", dir_name="calib_test")
            self.raw_image_count += 1

        if (position >= self.laser_calib_start and position <= self.laser_calib_end):
            flags = cv2.CALIB_CB_FAST_CHECK | cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
        else:
            flags = cv2.CALIB_CB_FAST_CHECK

        try:
            self._logger.debug("Trying to detect calibration pattern pose and plane.")
            pose = self._imageprocessor.detect_pose(pattern_image, flags)
            plane = self._imageprocessor.detect_pattern_plane(pose)
            self._logger.debug("Detected Plane: {0}, Detected Pose: {1}.".format(bool(pose), bool(plane)))

        except Exception as e:
            plane = None
            self._logger.error("Error while Scanner Calibration Capture: {0}".format(e))

        if plane is not None:

            distance, normal, corners = plane
            self._logger.debug("Calibration Pattern plane detected.")
            # Laser triangulation ( Between 60 and 115 degree )
            # angel/(360/3200)
            try:
                exc_info = sys.exc_info()
                #Laser Calibration
                alpha = np.rad2deg(math.acos(normal[2] / np.linalg.norm((normal[0], normal[2])))) * math.copysign(1, normal[0])

                self._logger.debug("Current Angle is: {0}".format(alpha))
                if ((abs(alpha) <= self.LASER_PLANE_CALIBRATION_START_POS_DEGREE) and (position > 0)):

                    self._hardwarecontroller.led.off()
                    for i in range(self.config.file.laser.numbers):

                        image = self._capture_laser(i)

                        if bool(self.config.file.keep_calibration_raw_images):
                            fs_image = FSImage()
                            fs_image.save_image(image, self.raw_image_count, "calibration", dir_name="calib_test")
                            self.raw_image_count += 1

                        if self.config.file.laser.interleaved == "True":
                            image = cv2.subtract(image, pattern_image)

                        image = self._imageprocessor.pattern_mask(image, corners)

                        # TODO: make  image saving contitional in confg --> calibration -> debug  ->  true/false
                        fs_image = FSImage()
                        fs_image.save_image(image, alpha, "laser_"+str(i), dir_name="calibration")

                        points_2d = self._imageprocessor.compute_2d_points(image, roi_mask=False, refinement_method='RANSAC')
                        point_3d = self._imageprocessor.compute_camera_point_cloud(points_2d, distance, normal)

                        if self._point_cloud[i] is None:
                            self._point_cloud[i] = point_3d.T
                        else:
                            self._point_cloud[i] = np.concatenate(
                                (self._point_cloud[i], point_3d.T))

                # Platform extrinsics
                origin = corners[self.config.file.calibration.pattern.columns * (self.config.file.calibration.pattern.rows - 1)][0]
                origin = np.array([[origin[0]], [origin[1]]])
                t = self._imageprocessor.compute_camera_point_cloud(
                    origin, distance, normal)

            except Exception as e:
                self._logger.exception(e)
                self._logger.error("Laser Capture Error: {0}".format(e))
                message = {
                    "message": "LASER_CALIBRATION_ERROR",
                    "level": "error"
                }
            #    #self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
                t = None


            if t is not None:
                self.x += [t[0][0]]
                self.y += [t[1][0]]
                self.z += [t[2][0]]

        if self.config.file.laser.interleaved == "False":
            self._hardwarecontroller.led.on(self.calibration_brightness[0], self.calibration_brightness[1], self.calibration_brightness[2])

    def _capture_pattern(self):
        #pattern_image = self._hardwarecontroller.get_pattern_image()
        time.sleep(1.5)
        pattern_image = self._hardwarecontroller.get_picture()
        pattern_image = self._imageprocessor.rotate_image(pattern_image)
        return pattern_image

    def _capture_laser(self, index):
        self._logger.debug("Capturing laser {0}".format(index))
        laser_image = self._hardwarecontroller.get_laser_image(index)
        laser_image = self._imageprocessor.rotate_image(laser_image)
        return laser_image

    def _calculate_scanner_calibration(self):
        response = None
        # Laser triangulation
        # Save point clouds
        for i in range(self.config.file.laser.numbers):
            self.save_point_cloud("CALIBRATION_{0}.ply".format(i), self._point_cloud[i])

        self.distance = [None, None]
        self.normal = [None, None]
        self.std = [None, None]

        # Compute planes
        for i in range(self.config.file.laser.numbers):
            plane = self.compute_plane(i, self._point_cloud[i])
            self.distance[i], self.normal[i], self.std[i] = plane

        # Platform extrinsics
        self.t = None
        self.x = np.array(self.x)
        self.y = np.array(self.y)
        self.z = np.array(self.z)
        points = list(zip(self.x, self.y, self.z))

        if len(points) > 4:
            # Fitting a plane
            point, normal = self.fit_plane(points)
            if normal[1] > 0:
                normal = -normal
            # Fitting a circle inside the plane
            center, self.R, circle = self.fit_circle(point, normal, points)
            # Get real origin
            self.t = center - self.config.file.calibration.pattern.origin_distance * np.array(normal)

            self._logger.info("Platform calibration ")
            self._logger.info(" Center Point: {0}".format(center))
            self._logger.info(" Translation: {0}".format(self.t))
            self._logger.info(" Rotation: {0}".format(str(self.R).replace('\n', '')))
            self._logger.info(" Normal: {0}".format(normal))

        # Return response
        result = True

        if self.t is not None and np.linalg.norm(self.t - self.estimated_t) < 200:
            response_platform_extrinsics = (
                self.R, self.t, center, point, normal, [self.x, self.y, self.z], circle)
        else:
            result = False

        response_laser_triangulation = []
        if self.std[0] is not None and self.std[0] < 1.0 and self.normal[0] is not None:
            response_laser_triangulation = [{"distance": self.distance[0], "normal":self.normal[0], "deviation":self.std[0]}]
            if self.std[1] is not None and self.std[1] < 1.0 and self.normal[1] is not None:
                response_laser_triangulation.append({"distance": self.distance[1], "normal": self.normal[1], "deviation": self.std[1]})
        else:
            result = False

        if result:
            self.config.file.calibration.platform_translation = copy.deepcopy(self.t)
            self.config.file.calibration.platform_rotation = copy.deepcopy(self.R)
            self.config.file.calibration.laser_planes = copy.deepcopy(response_laser_triangulation)
            response = (True, (response_platform_extrinsics, response_laser_triangulation))
        else:
            self._logger.exception("Calibration process was not able to estimate laser planes.")

            message = {
                    "message": "SCANNER_CALIBRATION_FAILED",
                    "level": "warn"
            }

            self._eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
            response = None

        return response


    def compute_plane(self, index, X):
        if X is not None and X.shape[0] > 3:
            model, inliers = self.ransac(X, PlaneDetection(), 3, 0.1)

            distance, normal, M = model
            std = np.dot(M.T, normal).std()

            self._logger.info("Laser calibration {0}".format(index))
            self._logger.info(" Distance: {0}".format(distance))
            self._logger.info(" Normal: {0}".format(normal))
            self._logger.info(" Standard deviation: {0}".format(std))
            self._logger.info(" Point cloud size: {0}".format(len(inliers)))

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
        for _ in range(max_trials):
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
            f = open(str(self.config.file.folders.scans)+'/calibration/'+str(filename), 'wb')
            self.save_point_cloud_stream(f, point_cloud)
            f.close()

    def save_point_cloud_stream(self, stream, point_cloud):
        frame = "ply\n"
        frame += "format binary_little_endian 1.0\n"
        frame += "comment Generated by FabScanPi software\n"
        frame += "element vertex {0}\n".format(str(len(point_cloud)))
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
            frame += str(struct.pack("<fffBBB", point[0], point[1], point[2], 255, 0, 0))
        stream.write(frame.encode(encoding='UTF-8'))

    def get_time_stamp(self):
        return int(datetime.now().strftime("%s%f"))/1000

import numpy.linalg


from scipy.sparse import linalg


class PlaneDetection(object):
    def fit(self, X):
        M, Xm = self._compute_m(X)
        U = linalg.svds(M, k=2)[0]
        normal = np.cross(U.T[0], U.T[1])
        #normal = numpy.linalg.svd(M)[0][:, 2]
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
