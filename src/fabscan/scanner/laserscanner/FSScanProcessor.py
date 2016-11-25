__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import datetime
import multiprocessing
import logging


from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface

from fabscan.util.FSUtil import FSSystem
from fabscan.file.FSPointCloud import FSPointCloud
from fabscan.FSEvents import FSEventManagerSingleton, FSEvents, FSEvent
from fabscan.vision.FSImageTask import ImageTask
from fabscan.vision.FSImageWorker import FSImageWorkerPool
from fabscan.util.FSInject import inject, singleton

from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorCommand


@singleton(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerSingleton,
    imageprocessor=ImageProcessorInterface,
    hardwarecontroller=FSHardwareControllerInterface
)
class FSScanProcessorSingleton(FSScanProcessorInterface):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller):
        super(FSScanProcessorInterface, self).__init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller)

        self.settings = settings
        self.config = config
        self._logger = logging.getLogger(__name__)

        self.eventmanager = eventmanager.instance

        # individual package classes for each of different scan method/priciple (e.g laser scan, kinect, etc.)
        self.hardwareController = hardwarecontroller
        self.image_processor = imageprocessor

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

        self.utils = FSSystem()

        self.semaphore = multiprocessing.BoundedSemaphore()
        self.event_q = self.eventmanager.get_event_q()

        self._worker_pool = FSImageWorkerPool(self.image_task_q, self.event_q)

        self._scan_brightness = self.settings.camera.brightness
        self._scan_contrast = self.settings.camera.contrast
        self._scan_saturation = self.settings.camera.saturation

        self.eventmanager.subscribe(FSEvents.ON_IMAGE_PROCESSED, self.image_processed)
        self._logger.info("Laser Scan Processor initilized...")


    def on_receive(self, event):
        if event[FSEvents.COMMAND] == FSScanProcessorCommand.START:
            self.start_scan()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.STOP:
            self.stop_scan()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.SETTINGS_MODE_ON:
            self.settings_mode_on()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.SETTINGS_MODE_OFF:
            self.settings_mode_off()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand._SCAN_NEXT_TEXTURE_POSITION:
            self.scan_next_texture_position()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION:
            self.scan_next_object_position()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.NOTIFY_HARDWARE_STATE:
            self.send_hardware_state_notification()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.UPDATE_SETTINGS:
            self.update_settings(event['SETTINGS'])

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_HARDWARE_INFO:
            return self.hardwareController.get_firmware_version()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_CALIBRATION_STREAM:
            return self.create_calibration_stream()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_LASER_STREAM:
            return self.create_laser_stream()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_TEXTURE_STREAM:
            return self.create_texture_stream()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.CALIBRATE_SCANNER:
            return self.calibrate_scanner()

    def create_texture_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self.image_processor.get_texture_stream_frame(image)
            return image
        except StandardError, e:
            #self._logger.error(e)
            pass

    def create_calibration_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self.image_processor.get_calibration_stream_frame(image)
            return image
        except StandardError, e:
            # images are dropped this cateched exception.. no error hanlder needed here.
            pass

    def create_laser_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self.image_processor.get_laser_stream_frame(image)
            return image
        except StandardError, e:
            # images are dropped this cateched exception.. no error hanlder needed here.
            pass


    def update_settings(self, settings):
        try:
            self.settings.update(settings)
            self.hardwareController.led.on(self.settings.led.red, self.settings.led.green, self.settings.led.blue)
        except StandardError, e:
            # images are dropped this cateched exception.. no error hanlder needed here.
            pass

    def calibrate_scanner(self):

        message = {
            "message": "START_CALIBRATION",
            "level": "info"
        }
        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        self.hardwareController.led.on(self.config.texture_illumination, self.config.texture_illumination, self.config.texture_illumination)
        self.hardwareController.start_camera_stream()


        # do calibration here....
        time.sleep(10)

        self.hardwareController.stop_camera_stream()
        self.hardwareController.led.off()

        event = FSEvent()
        event.command = 'CALIBRATION_COMPLETE'
        self.eventmanager.publish(FSEvents.COMMAND, event)

        #self.hardwareController.calibrate_scanner()

        message = {
            "message": "FINISHED_CALIBRATION",
            "level": "info"
        }
        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def send_hardware_state_notification(self):
        self._logger.debug("Checking Hardware connections")

        if not self.hardwareController.arduino_is_connected():
            message = {
                "message": "NO_SERIAL_CONNECTION",
                "level": "error"
            }

            self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        if not self.hardwareController.camera_is_connected():
            message = {
                "message": "NO_CAMERA_CONNECTION",
                "level": "error"
            }

            self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def settings_mode_on(self):
        self.hardwareController.settings_mode_on()

    def settings_mode_off(self):
        self.hardwareController.settings_mode_off()

    def start_scan(self):
        self.settings_mode_off()
        self._logger.info("Scan started")
        self._stop_scan = False

        self.hardwareController.turntable.enable_motors()

        self._resolution = int(self.settings.resolution)
        self._laser_positions = int(self.settings.laser_positions)
        self._is_color_scan = bool(self.settings.color)

        self._number_of_pictures = 3200 / int(self.settings.resolution)
        self.current_position = 0

        # TODO: rename prefix to scan_id
        self._prefix = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
        self.point_cloud = FSPointCloud(color=self._is_color_scan)


        if self._is_color_scan:
            self._total = self._number_of_pictures * 2
            self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_TEXTURE_POSITION})
        else:
            self._total = self._number_of_pictures
            self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION})

    def init_texture_scan(self):
        message = {
            "message": "SCANNING_TEXTURE",
            "level": "info"
        }
        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self._worker_pool.create(self.config.process_numbers)

        self._scan_brightness = self.settings.camera.brightness
        self._scan_contrast = self.settings.camera.contrast
        self._scan_saturation = self.settings.camera.saturation

        self.settings.camera.brightness = 50
        self.settings.camera.contrast = 0
        self.settings.camera.saturation = 0
        self.hardwareController.led.on(self.config.texture_illumination, self.config.texture_illumination, self.config.texture_illumination)
        time.sleep(1)
        self.hardwareController.camera.device.startStream(auto_exposure=True)
        time.sleep(2)

        #time.sleep(2)

    def finish_texture_scan(self):
        self._logger.info("Finishing texture scan.")
        self.current_position = 0
        self.hardwareController.led.off()

        self.settings.camera.brightness = self._scan_brightness
        self.settings.camera.contrast = self._scan_contrast
        self.settings.camera.saturation = self._scan_saturation

        self.hardwareController.camera.device.stopStream()
        self.hardwareController.camera.device.flushStream()
        time.sleep(0.8)

        self._worker_pool.kill()

    def scan_next_texture_position(self):
        if not self._stop_scan:
            if self.current_position <= self._number_of_pictures:
                if self.current_position == 0:
                    self.init_texture_scan()

                color_image = self.hardwareController.scan_at_position(self._resolution, color=True)
                task = ImageTask(color_image, self._prefix, self.current_position, self._number_of_pictures, task_type="PROCESS_COLOR_IMAGE")
                self.image_task_q.put(task, True)
                #self._logger.debug("Color Progress %i of %i : " % (self.current_position, self._number_of_pictures))
                self.current_position += 1
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_TEXTURE_POSITION})
            else:
                self.finish_texture_scan()
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION})

    def init_object_scan(self):
        self._logger.info("Started object scan initialisation")

        self.current_position = 0

        self._laser_positions = self.settings.laser_positions

        self.hardwareController.led.on(self.settings.led.red, self.settings.led.green, self.settings.led.blue)
        self.hardwareController.laser.on()
        time.sleep(0.5)
        self.hardwareController.camera.device.startStream()
        self.hardwareController.camera.device.flushStream()
        time.sleep(0.5)

        #self._laser_angle = self.image_processor.calculate_laser_angle(self.hardwareController.camera.device.getFrame())
        self._laser_angle = self.settings.backwall.laser_angle

        if self._laser_angle == None:
            event = FSEvent()
            event.command = 'SCANNER_ERROR'
            self.eventmanager.publish(FSEvents.COMMAND,event)
            self.on_laser_detection_failed()
            self._logger.debug("Send laser detection failure event")
        else:
            message = {
                "message": "SCANNING_OBJECT",
                "level": "info"
            }
            self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
            self._logger.debug("Detected Laser Angle at: %f deg" % (self._laser_angle,))
            self._worker_pool.create(self.config.process_numbers)

    def finish_object_scan(self):
        self._logger.info("Finishing object scan.")
        self._worker_pool.kill()
        self.hardwareController.laser.off()
        self.hardwareController.led.off()
        self.hardwareController.camera.device.stopStream()


    def scan_next_object_position(self):
        if not self._stop_scan:
            if self.current_position <= self._number_of_pictures:
                if self.current_position == 0:
                    self.init_object_scan()

                laser_image = self.hardwareController.scan_at_position(self._resolution)
                task = ImageTask(laser_image, self._prefix, self.current_position, self._number_of_pictures)
                self.image_task_q.put(task)
                #self._logger.debug("Laser Progress: %i of %i at laser position %i" % (
                #   self.current_position, self._number_of_pictures, self._current_laser_position
                #))
                self.current_position += 1
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION})

            else:
                self.finish_object_scan()

    def on_laser_detection_failed(self):

        self._logger.info("Send laser detection failed message to frontend")
        message = {
            "message": "NO_LASER_FOUND",
            "level": "warn"
        }

        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.settings_mode_on()

    def stop_scan(self):
        self._stop_scan = True
        self._worker_pool.kill()
        time.sleep(1)
        self.utils.delete_scan(self._prefix)
        self.reset_scanner_state()
        self._logger.info("Scan stoped")
        self.hardwareController.camera.device.stopStream()

        message = {
            "message": "SCAN_CANCELED",
            "level": "info"
        }
        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def image_processed(self, eventmanager, event):

        if event['image_type'] == 'depth':
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

        self.eventmanager.broadcast_client_message(FSEvents.ON_NEW_PROGRESS, message)

    def scan_complete(self):

        self._logger.info("Scan complete writing pointcloud files with %i points." % (self.point_cloud.get_size(),))
        self.point_cloud.saveAsFile(self._prefix)
        settings_filename = self.config.folders.scans+self._prefix+"/"+self._prefix+".fab"
        self.settings.saveAsFile(settings_filename)

        message = {
            "message": "SAVING_POINT_CLOUD",
            "scan_id": self._prefix,
            "level": "info"
        }

        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        self.utils.delete_image_folders(self._prefix)
        self.reset_scanner_state()

        event = FSEvent()
        event.command = 'COMPLETE'
        self.eventmanager.publish(FSEvents.COMMAND,event)

        message = {
            "message": "SCAN_COMPLETE",
            "scan_id": self._prefix,
            "level": "success"
        }

        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.hardwareController.camera.device.stopStream()

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
        self.hardwareController.camera.device.flushStream()
        self.hardwareController.laser.off()
        self.hardwareController.led.off()
        self.hardwareController.turntable.disable_motors()
        self._command = None
        self._progress = 0
        self.current_position = 0
        self._number_of_pictures = 0
        self._total = 0
