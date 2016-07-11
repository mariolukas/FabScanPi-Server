__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import datetime
import multiprocessing
import logging
from fabscan.util import FSUtil
from fabscan.file.FSPointCloud import FSPointCloud
from fabscan.FSEvents import FSEventManager, FSEvents, FSEvent
from fabscan.vision.FSImageTask import ImageTask
from fabscan.vision.FSImageProcessor import ImageProcessor
from fabscan.vision.FSImageWorker import FSImageWorkerPool
from fabscan.hardware.FSHardwareControllerFactory import FSHardwareControllerFactory
from fabscan.vision.FSImageProcessorFactory import FSImageProcessorFactory
from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings
from fabscan.scanner.FSAbstractScanProcessor import FSAbstractScanProcessor
from fabscan.scanner.FSAbstractScanProcessor import FSScanProcessorCommand
from fabscan.hardware.FSLaserScannerHardwareController import FSLaserScannerHardwareController

class FSLaserScanProcessor(FSAbstractScanProcessor):
    def __init__(self):
        super(FSLaserScanProcessor, self).__init__()

        self.eventManager = FSEventManager.instance()
        self.settings = Settings.instance()
        self.config = Config.instance()

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self._prefix = None
        self._resolution = 16
        self._number_of_pictures = 0
        self._total = 0
        self._laser_positions = 1
        self._progress = 0
        self._is_color_scan = True
        self.point_cloud = None
        self.image_task_q = multiprocessing.Queue(self.config.process_numbers + 1)
        self.current_position = 0
        self._laser_angle = 33.0
        self._stop_scan = False
        self._current_laser_position = 1

        self.semaphore = multiprocessing.BoundedSemaphore()
        self.event_q = self.eventManager.get_event_q()

        self._worker_pool = FSImageWorkerPool(self.image_task_q, self.event_q)
        self.hardwareController = FSHardwareControllerFactory.get_hardware_controller_instance(self.config.scanner_type)
        self.eventManager.subscribe(FSEvents.ON_IMAGE_PROCESSED, self.image_processed)
        self._scan_brightness = self.settings.camera.brightness
        self._scan_contrast = self.settings.camera.contrast
        self._scan_saturation = self.settings.camera.saturation


    def get_hardware_info(self):
        return str(self.hardwareController.get_firmware_version())

    def update_settings(self, settings):
        try:
            self.settings.update(settings)
            self.hardwareController.led.on(self.settings.led.red, self.settings.led.green, self.settings.led.blue)
        except:
            pass

    def send_hardware_state_notification(self):

            self._logger.debug("Checking Hardware connections")

            if not self.hardwareController.arduino_is_connected():
                message = {
                    "message": "NO_SERIAL_CONNECTION",
                    "level": "error"
                }
            else:
                message = {
                    "message": "SERIAL_CONNECTION_READY",
                    "level": "info"
                }

            self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

            if not self.hardwareController.camera_is_connected():
                message = {
                    "message": "NO_CAMERA_CONNECTION",
                    "level": "error"
                }
            else:
                message = {
                    "message": "CAMERA_READY",
                    "level": "info"
                }

            self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)


    def settings_mode_on(self):
        self.hardwareController.settings_mode_on()

    def settings_mode_off(self):
        self.hardwareController.camera.stopStream()
        self.hardwareController.settings_mode_off()

    def start_scan(self):
        self.hardwareController.settings_mode_off()
        self._logger.info("Scan started")
        self._stop_scan = False
        self.hardwareController.laser.off()
        self.hardwareController.turntable.stop_turning()
        self.hardwareController.turntable.enable_motors()
        self.hardwareController.camera.startStream()
        self._resolution = int(self.settings.resolution)
        self._laser_positions = int(self.settings.laser_positions)
        self._is_color_scan = bool(self.settings.color)

        self._number_of_pictures =  self.config.turntable.steps / int(self.settings.resolution)
        self.current_position = 0

        # TODO: rename prefix to scan_id
        self._prefix = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
        self.point_cloud = FSPointCloud(self._is_color_scan)
        self.image_processor = FSImageProcessorFactory.get_image_processor_class(self.config.scanner_type)
        #self.image_processor = ImageProcessor(self.config, self.settings)

        if self._is_color_scan:
            self._total = self._number_of_pictures * 2
            self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand.SCAN_NEXT_TEXTURE_POSITION})
        else:
            self._total = self._number_of_pictures
            self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand.SCAN_NEXT_OBJECT_POSITION})

    def init_texture_scan(self):
        message = {
            "message": "SCANNING_TEXTURE",
            "level": "info"
        }
        self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self._worker_pool.create(self.config.process_numbers)

        self._scan_brightness = self.settings.camera.brightness
        self._scan_contrast = self.settings.camera.contrast
        self._scan_saturation = self.settings.camera.saturation

        self.hardwareController.camera.textureExposureMode()
        self.settings.camera.brightness = 50
        self.settings.camera.contrast = 0
        self.settings.camera.saturation = 0

        self.hardwareController.led.on(20, 20, 20)
        time.sleep(4)
        self.hardwareController.camera.flushStream()
        time.sleep(1)

    def finish_texture_scan(self):
        self._logger.info("Finishing texture scan.")
        self.current_position = 0
        self.hardwareController.led.off()
        self.settings.camera.brightness = self._scan_brightness
        self.settings.camera.contrast = self._scan_contrast
        self.settings.camera.saturation = self._scan_saturation
        self._worker_pool.kill()

    def scan_next_texture_position(self):
        if not self._stop_scan:
            if self.current_position < self._number_of_pictures:
                if self.current_position == 0:
                    self.init_texture_scan()

                color_image = self.hardwareController.scan_at_position(self._resolution, color=True)
                task = ImageTask(color_image, self._prefix, self.current_position, self._number_of_pictures, task_type="PROCESS_COLOR_IMAGE")
                self.image_task_q.put(task, True)
                self._logger.debug("Color Progress %i of %i : " % (self.current_position, self._number_of_pictures))
                self.current_position += 1
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand.SCAN_NEXT_TEXTURE_POSITION})
            else:
                self.finish_texture_scan()
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand.SCAN_NEXT_OBJECT_POSITION})

    def init_object_scan(self):
        self._logger.debug("Started object scan initialisation")

        self.current_position = 0

        self._laser_positions = self.settings.laser_positions
        self.hardwareController.led.on(self.settings.led.red, self.settings.led.green, self.settings.led.blue)

        self.hardwareController.laser.on()

        self.settings.camera.brightness = self._scan_brightness
        self.settings.camera.contrast = self._scan_contrast
        self.settings.camera.saturation = self._scan_saturation

        # TODO: solve this timing issue!
        # Workaround for Logitech webcam. We have to wait a loooong time until the logitech cam is ready...
        # time.sleep(3)

        self.hardwareController.camera.objectExposureMode()
        self.hardwareController.camera.flushStream()
        time.sleep(2)

        self._laser_angle = self.image_processor.calculate_laser_angle(self.hardwareController.camera.getFrame())

        if self._laser_angle == None:
            event = FSEvent()
            event.command = 'SCANNER_ERROR'
            self.eventManager.publish(FSEvents.COMMAND,event)
            self.on_laser_detection_failed()
            self._logger.debug("Send laser detection failure event")
        else:
            message = {
                "message": "SCANNING_OBJECT",
                "level": "info"
            }
            self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
            self._logger.debug("Detected Laser Angle at: %f deg" % (self._laser_angle,))
            self._worker_pool.create(self.config.process_numbers)

    def finish_object_scan(self):
        self._logger.info("Finishing object scan.")
        self._worker_pool.kill()
        self.hardwareController.laser.off()
        self.hardwareController.led.off()
        self.hardwareController.camera.setPreviewResolution()

    def scan_next_object_position(self):
        if not self._stop_scan:
            if self.current_position < self._number_of_pictures:
                if self.current_position == 0:
                    self.init_object_scan()

                laser_image = self.hardwareController.scan_at_position(self._resolution)
                task = ImageTask(laser_image, self._prefix, self.current_position, self._number_of_pictures)
                self.image_task_q.put(task)
                self._logger.debug("Laser Progress: %i of %i at laser position %i" % (
                self.current_position, self._number_of_pictures, self._current_laser_position))
                self.current_position += 1
                self.actor_ref.tell({FSEvents.COMMAND: 'SCAN_NEXT_OBJECT_POSITION'})

            else:
                self.finish_object_scan()

    def on_laser_detection_failed(self):

        self._logger.info("Send laser detection failed message to frontend")
        message = {
            "message": "NO_LASER_FOUND",
            "level": "warn"
        }

        self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.settings_mode_on()

    def stop_scan(self):
        self._stop_scan = True
        self._worker_pool.kill()
        time.sleep(1)
        FSUtil.delete_scan(self._prefix)
        self.reset_scanner_state()
        self._logger.info("Scan stoped")
        self.hardwareController.camera.stopStream()

        message = {
            "message": "SCAN_CANCELED",
            "level": "info"
        }
        self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def image_processed(self, eventManager, event):

        if event['image_type'] == 'laser':
            self.append_points(event['points'])

        self.semaphore.acquire()
        self._progress += 1
        self.semaphore.release()

        message = {
            "points": event['points'],
            "progress": self._progress,
            "resolution": self._total
        }

        if self._progress == self._total:
            self.scan_complete()

        self.eventManager.broadcast_client_message(FSEvents.ON_NEW_PROGRESS, message)

    def scan_complete(self):

        self._logger.debug("Scan complete writing pointcloud files with %i points." % (self.point_cloud.get_size(),))
        self.point_cloud.saveAsFile(self._prefix)
        self.settings.saveAsFile(self._prefix)

        message = {
            "message": "SAVING_POINT_CLOUD",
            "scan_id": self._prefix,
            "level": "info"
        }

        self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        FSUtil.delete_image_folders(self._prefix)
        self.reset_scanner_state()

        event = FSEvent()
        event.command = 'COMPLETE'
        self.eventManager.publish(FSEvents.COMMAND,event)

        message = {
            "message": "SCAN_COMPLETE",
            "scan_id": self._prefix,
            "level": "success"
        }

        self.eventManager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.hardwareController.camera.stopStream()

    def append_points(self, point_set):
        if self.point_cloud:
            for point in point_set:
                self.point_cloud.append_point(point)

    def get_resolution(self):
        return self.settings.resolution

    def get_number_of_pictures(self):
        return self._number_of_pictures

    def get_folder_name(self):
        return self._prefix

    def reset_scanner_state(self):
        self._logger.info("Reseting scanner states ... ")
        self.hardwareController.camera.objectExposureMode()
        #self.hardwareController.camera.flushStream()
        self.hardwareController.laser.off()
        self.hardwareController.led.off()
        self.hardwareController.turntable.disable_motors()
        self._command = None
        self._progress = 0
        self.current_position = 0
        self._number_of_pictures = 0
        self._total = 0
