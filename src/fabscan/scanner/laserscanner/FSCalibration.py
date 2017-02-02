
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

        self._logger = logging.getLogger(__name__)
        self._logger.debug("Calibration System Initialized")

        # termination criteria
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(columns-1,rows-1,0)
        self.objp = np.zeros((self.rows * self.columns, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.columns, 0:self.rows].T.reshape(-1, 2)


    def start(self):
        self.camera(with_laser=False)

        images = sorted(glob.glob(self.config.folders.scans + '/calibration/calibration_*.jpg'))
        self._logger.debug(len(images))
        error, mtx, dist, chessboards = self.compute_calibration(images)

        self._logger.debug("Number of samples {0}".format(len(images)))
        self._logger.debug("Calibration error {0}".format(error))
        self._logger.debug("Camera matrix {0}".format(mtx))
        self._logger.debug("Distortion coefficients{0}".format(dist))
        self._logger.debug("Set of images")
        #self.camera(with_laser=True)


    def camera(self, with_laser=False):
        self._hardwarecontroller.laser.off()
        image = FSImage()
        self._logger.debug("Camera Calibration started... ")
        laser_prefix = ''
        if with_laser:
            laser_prefix = '_with_laser'
            self._hardwarecontroller.laser.on()

        self._hardwarecontroller.led.on(150, 150, 150)
        self._hardwarecontroller.start_camera_stream()
        time.sleep(1)

        self._logger.debug("Cam is ready for calibration...")

        calibration_steps = 10
        steps_for_quater_turn = self.config.turntable.steps/8
        motor_steps = steps_for_quater_turn / calibration_steps

        for x in range(0, steps_for_quater_turn, steps_for_quater_turn/calibration_steps):

            img = self._hardwarecontroller.get_picture()
            image.save_image(img, str(x)+"_left", 'calibration'+laser_prefix, dir_name='/calibration/')
            self._logger.debug("STEP FF "+str(x))
            self._hardwarecontroller.turntable.step_blocking(motor_steps, 900)
            time.sleep(1)

        self._hardwarecontroller.turntable.step_blocking(-motor_steps*calibration_steps, 900)
        time.sleep(3)

        for x in range(0, steps_for_quater_turn, steps_for_quater_turn / calibration_steps):
            img = self._hardwarecontroller.get_picture()
            image.save_image(img, str(x)+"_right", 'calibration'+laser_prefix, dir_name='/calibration/')
            self._hardwarecontroller.turntable.step_blocking(-motor_steps, 100)
            self._logger.debug("STEP REV "+str(x))
            time.sleep(1)

        self._hardwarecontroller.turntable.step_blocking(motor_steps*calibration_steps, 900)


        self._hardwarecontroller.stop_camera_stream()
        self._hardwarecontroller.led.off()
        self._hardwarecontroller.laser.off()

    def compute_calibration(self, images):
        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.
        chessboards = []  # images with chessboard painted

        for fname in images:

            img = cv2.imread(fname)
            img = cv2.transpose(img)
            img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (self.columns, self.rows), None)

            # If found, add object points, image points (after refining them)
            if ret:
                objpoints.append(self.objp)

                # Perform corner subpixel detection
                cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
                imgpoints.append(corners)

                # Show chessboards detected
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                cv2.drawChessboardCorners(img, (self.columns, self.rows), corners, ret)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                chessboards.append(img)

        # Perform camera calibration
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        # Compute calibration error
        n = len(objpoints)
        error = 0
        for i in range(n):
            imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error += cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / (len(imgpoints2))
        error /= n

        return error, mtx, dist, chessboards