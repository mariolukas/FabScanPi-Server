
import cv2
import numpy as np
from PIL import Image
import time
import logging
from fabscan.util.FSInject import singleton
import glob

from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.FSEvents import FSEventManagerSingleton
from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.scanner.interfaces.FSCalibration import FSCalibrationInterface
from fabscan.file.FSImage import FSImage

#focal_pixel = (focal_mm / sensor_width_mm) * image_width_in_pixels

#And if you know the horizontal field of view, say in degrees,

#focal_pixel = (image_width_in_pixels * 0.5) / tan(FOV * 0.5 * PI/180)


@singleton(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerSingleton,
    imageprocessor=ImageProcessorInterface,
    hardwarecontroller=FSHardwareControllerInterface

)
class FSCalibrationSingleton(FSCalibrationInterface):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller):
        #super(FSCalibrationInterface, self).__init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller)

        self._imageprocessor = imageprocessor
        self._hardwarecontroller = hardwarecontroller
        self.config = config
        self.settings = settings

        self.rows = 6
        self.columns = 11
        self.square_size = 11

        # termination criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.pattern_points = None
        self.pattern_size = None
        self.obj_points = []
        self.image_points = []

        self._logger = logging.getLogger(__name__)
        self._logger.debug("Calibration System Initialized")


    def init_pattern_points(self):
        self.pattern_size = (self.columns, self.rows)
        self.pattern_points = np.zeros((np.prod(self.pattern_size), 3), np.float32)
        self.pattern_points[:, :2] = np.indices(self.pattern_size).T.reshape(-1, 2)
        self.pattern_points *= self.square_size


    def start_calibration(self):

        self.init_pattern_points()
        self.capture_images()
        self.do_camera_calibration()
        self.do_pose_detection()
        self.config.save()


    def load_calibration_images(self):
        images = sorted(glob.glob(self.config.folders.scans + '/calibration/laser_off/calibration_*.jpg'))
        return images

    def do_camera_calibration(self):
        images = self.load_calibration_images()
        h, w = 0, 0
        img_names_undistort = []
        for fn in images:
            #self._logger.debug('processing %s... ' % fn, end='')
            img = cv2.imread(fn, 0)
            if img is None:
                self._logger.debug("Failed to load", fn)
                continue

            h, w = img.shape[:2]
            found, corners = cv2.findChessboardCorners(img, self.pattern_size)
            if found:
                term = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 30, 0.1)
                cv2.cornerSubPix(img, corners, (11, 11), (-1, -1), term)

            #if debug_dir:
            #    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            #    cv2.drawChessboardCorners(vis, pattern_size, corners, found)
            #    path, name, ext = splitfn(fn)
            #    outfile = debug_dir + name + '_chess.png'
            #    cv2.imwrite(outfile, vis)
            #    if found:
            #        img_names_undistort.append(outfile)

            if not found:
                self._logger.debug('chessboard not found')
                continue

            self.image_points.append(corners.reshape(-1, 2))
            self.obj_points.append(self.pattern_points)

            self._logger.debug('ok')

        # calculate camera distortion
        rms, camera_matrix, dist_coefficients, rvecs, tvecs = cv2.calibrateCamera(self.obj_points, self.image_points, (w, h), None, None)

        self.config.calibration.camera_matrix = camera_matrix
        self.config.calibration.dist_coefficients = dist_coefficients


        self._logger.debug("RMS:" + str(rms))
        self._logger.debug("camera matrix:" + str(camera_matrix))
        self._logger.debug("distortion coefficients: " + str(dist_coefficients.ravel()))

    def do_pose_detection(self):
        images = self.load_calibration_images()
        fn = images.pop((len(images) - 1) // 2)
        image = cv2.imread(fn)
        h, w, c = image.shape

        newcamera, roi = cv2.getOptimalNewCameraMatrix(self.config.calibration.camera_matrix, self.config.calibration.dist_coefficients, (w, h), 0)
        image = cv2.undistort(image, self.config.calibration.camera_matrix, self.config.calibration.dist_coefficients, newcamera, None)

        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, self.pattern_size, None)

        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # while(True):
        #    cv2.imshow('img',gray)
        #    cv2.waitKey(500)
        # Find corners with subpixel accuracy
        cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

        # Compute pose
        ret, rvecs, tvecs = cv2.solvePnP(self.pattern_points, corners, self.config.calibration.camera_matrix, self.config.calibration.dist_coefficients)

        if ret:
            R = cv2.Rodrigues(rvecs)[0]
            t = tvecs.T[0]
            n = R.T[2]
            d = np.dot(n, t)
            self._logger.debug("Rotation matrix {0}".format(R))
            self._logger.debug("Translation vector {0} mm".format(t))
            self._logger.debug("Plane normal {0}".format(n))
            self._logger.debug("Plane distance {0} mm".format(d))

        self.config.calibration.plane.distance = d
        self.config.calibration.plane.normal = n
        self.config.calibration.plane.rotation = R
        self.config.calibration.plane.translation = t

    def capture_images(self):
        self._logger.debug("Camera Calibration started... ")
        self._hardwarecontroller.led.on(110, 110, 110)
        time.sleep(1)
        self._hardwarecontroller.laser.off()
        self._hardwarecontroller.start_camera_stream()
        time.sleep(1)

        image = FSImage()

        sub_dir = 'laser_off/'


        calibration_steps = 15
        steps_for_quater_turn = self.config.turntable.steps / 8
        motor_steps = steps_for_quater_turn / calibration_steps

        self._hardwarecontroller.turntable.step_blocking(-steps_for_quater_turn, 900)
        time.sleep(2)

        i = 0
        for x in range(0, steps_for_quater_turn*2, steps_for_quater_turn / calibration_steps):
            img = self._hardwarecontroller.get_picture()
            image.save_image(img, str(i), 'calibration', dir_name='/calibration/' + sub_dir)
            self._hardwarecontroller.turntable.step_blocking(motor_steps, 900)
            time.sleep(2)
            i=i+1


        self._hardwarecontroller.turntable.step_blocking(-steps_for_quater_turn, 900)
        time.sleep(2)

        self._hardwarecontroller.stop_camera_stream()
        self._hardwarecontroller.led.off()
        self._hardwarecontroller.laser.off()
