__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import time
import multiprocessing
import logging
from datetime import datetime

from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface

from fabscan.lib.util.FSUtil import FSSystem
from fabscan.lib.file.FSPointCloud import FSPointCloud
from fabscan.FSEvents import FSEventManagerSingleton, FSEvents, FSEvent
from fabscan.worker.FSImageTask import ImageTask
from fabscan.worker.FSImageWorker import FSImageWorkerPool
from fabscan.lib.util.FSInject import inject, singleton

from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorCommand
from fabscan.scanner.interfaces.FSCalibration import FSCalibrationInterface

@singleton(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerSingleton,
    imageprocessor=ImageProcessorInterface,
    hardwarecontroller=FSHardwareControllerInterface,
    calibration=FSCalibrationInterface
)
class FSScanProcessor(FSScanProcessorInterface):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller, calibration):
        super(FSScanProcessorInterface, self).__init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller, calibration)

        self.settings = settings
        self.config = config
        self._logger = logging.getLogger(__name__)

        self.eventmanager = eventmanager.instance
        self.calibration = calibration

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
        self.image_task_q = multiprocessing.Queue(self.config.process_numbers*2)
        self.current_position = 0
        self._stop_scan = False
        self._current_laser_position = 1
        self._starttime = 0

        self.utils = FSSystem()

        self.semaphore = multiprocessing.BoundedSemaphore()
        self.event_q = self.eventmanager.get_event_q()

        self._worker_pool = None

        self._scan_brightness = self.settings.camera.brightness
        self._scan_contrast = self.settings.camera.contrast
        self._scan_saturation = self.settings.camera.saturation

        self.eventmanager.subscribe(FSEvents.ON_IMAGE_PROCESSED, self.image_processed)

        self._logger.info("Laser Scan Processor initilized..."+str(self))


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

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.UPDATE_CONFIG:
            self.update_settings(event['CONFIG'])

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_HARDWARE_INFO:
            return self.hardwareController.get_firmware_version()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_ADJUSTMENT_STREAM:
            return self.create_adjustment_stream()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_LASER_STREAM:
            return self.create_laser_stream()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_TEXTURE_STREAM:
            return self.create_texture_stream()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_CALIBRATION_STREAM:
            return self.create_calibration_stream()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.START_CALIBRATION:
            return self.start_calibration()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.STOP_CALIBRATION:
            return self.stop_calibration()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.NOTIFY_IF_NOT_CALIBRATED:
            return self.notify_if_is_not_calibrated()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.CALL_HARDWARE_TEST_FUNCTION:
            device = event['DEVICE_TEST']
            self.hardwareController.call_test_function(device)


    def call_hardware_test_function(self, function):
        self.hardwareController.call_test_function(function)

    def notify_if_is_not_calibrated(self):
        self._logger.debug(self.config.calibration.camera_matrix)
        is_calibrated = not (self.config.calibration.laser_planes[0]['normal'] == [])
        self._logger.debug("FabScan is calibrated: "+str(is_calibrated))

        if not is_calibrated:
            message = {
                "message": "SCANNER_NOT_CALIBRATED",
                "level": "warn"
            }

            self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def create_texture_stream(self):
        try:
            image = self.hardwareController.get_picture()
            #image = self.image_processor.get_texture_stream_frame(image)
            return image
        except StandardError, e:
            #self._logger.error(e)
            pass

    def create_adjustment_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self.image_processor.get_adjustment_stream_frame(image)
            return image
        except StandardError, e:
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

            return image
        except StandardError, e:
            # images are dropped this cateched exception.. no error hanlder needed here.
            pass


    def update_settings(self, settings):
        try:
            self.settings.update(settings)
            #FIXME: Only change Color Settings when values changed.
            self.hardwareController.led.on(self.settings.led.red, self.settings.led.green, self.settings.led.blue)
        except StandardError, e:
            # images are dropped this cateched exception.. no error hanlder needed here.
            pass

    def update_config(self, config):
        try:
            self.config.update(config)
        except StandardError, e:
            pass

    def start_calibration(self):
        self.hardwareController.settings_mode_off()
        time.sleep(0.5)
        self.calibration.start()

    def stop_calibration(self):
        self.calibration.stop()

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
        #message = {
        #    "message": "SETTINGS_MODE_ON",
        #    "level": "info"
        #}
        #self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.hardwareController.settings_mode_on()

    def settings_mode_off(self):
        #message = {
        #    "message": "SETTINGS_MODE_OFF",
        #    "level": "info"
        #}
        #self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.hardwareController.settings_mode_off()

    def start_scan(self):
        self.settings_mode_off()
        self._logger.info("Scan started")
        self._stop_scan = False

        if self._worker_pool is None:
            self._worker_pool = FSImageWorkerPool(self.image_task_q, self.event_q)

        self.hardwareController.turntable.enable_motors()
        self.hardwareController.start_camera_stream(mode="default")
        time.sleep(1.5)
        self._resolution = int(self.settings.resolution)
        self._laser_positions = int(self.settings.laser_positions)
        self._is_color_scan = bool(self.settings.color)

        self._number_of_pictures = self.config.turntable.steps / int(self.settings.resolution)
        self.current_position = 0
        self._starttime = self.get_time_stamp()

        # TODO: rename prefix to scan_id
        self._prefix = datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
        self.point_cloud = FSPointCloud(color=self._is_color_scan)

        if not (self.config.calibration.laser_planes[0]['normal'] == []) and self.actor_ref.is_alive():
            if self._is_color_scan:
                self._total = self._number_of_pictures * 2 * self.config.laser.numbers
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_TEXTURE_POSITION})
            else:
                self._total = self._number_of_pictures * self.config.laser.numbers
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION})
        else:
            self._logger.debug("FabScan is not calibrated scan canceled")

            message = {
                "message": "SCANNER_NOT_CALIBRATED",
                "level": "warn"
            }

            self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

            event = FSEvent()
            event.command = 'STOP'
            self.eventmanager.publish(FSEvents.COMMAND, event)

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

        #self.settings.camera.brightness = 50
        #self.settings.camera.contrast = 0
        #self.settings.camera.saturation = 0
        self.hardwareController.led.on(self.config.texture_illumination, self.config.texture_illumination, self.config.texture_illumination)

        self.hardwareController.camera.device.flush_stream()


    def finish_texture_scan(self):
        self._logger.info("Finishing texture scan.")
        self.current_position = 0
        self.hardwareController.camera.device.flush_stream()

        self.hardwareController.led.off()

        self.settings.camera.brightness = self._scan_brightness
        self.settings.camera.contrast = self._scan_contrast
        self.settings.camera.saturation = self._scan_saturation

    def scan_next_texture_position(self):
        if not self._stop_scan:
            if self.current_position <= self._number_of_pictures and self.actor_ref.is_alive():
                if self.current_position == 0:
                    self.init_texture_scan()

                color_image = self.hardwareController.scan_at_position(self._resolution, color=True)
                task = ImageTask(color_image, self._prefix, self.current_position, self._number_of_pictures, task_type="PROCESS_COLOR_IMAGE")
                self.image_task_q.put(task, True)
                #self._logger.debug("Color Progress %i of %i : " % (self.current_position, self._number_of_pictures))
                self.current_position += 1
                if self.actor_ref.is_alive():
                    self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_TEXTURE_POSITION})
            else:
                while not self.image_task_q.empty():
                    # wait until texture scan stream is ready.
                    time.sleep(0.1)

                self.finish_texture_scan()
                if self.actor_ref.is_alive():
                    self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION})

    def init_object_scan(self):
        self._logger.info("Started object scan initialisation")

        message = {
            "message": "SCANNING_OBJECT",
            "level": "info"
        }
        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        self.current_position = 0
        self._laser_positions = self.settings.laser_positions
        # wait for ending of texture stream

        self.hardwareController.led.on(self.settings.led.red, self.settings.led.green, self.settings.led.blue)
        self.hardwareController.laser.on()

        self.hardwareController.camera.device.flush_stream()
        time.sleep(2)
        if not self._worker_pool.workers_active():
            self._worker_pool.create(self.config.process_numbers)

    def finish_object_scan(self):
        self._logger.info("Finishing object scan.")
        self._worker_pool.kill()

    def scan_next_object_position(self):
        if not self._stop_scan:
            if self.current_position <= self._number_of_pictures and self.actor_ref.is_alive():
                if self.current_position == 0:
                    self.init_object_scan()

                laser_image = self.hardwareController.scan_at_position(self._resolution)
                task = ImageTask(laser_image, self._prefix, self.current_position, self._number_of_pictures)
                self.image_task_q.put(task)
                self._logger.debug("Laser Progress: %i of %i at laser position %i" % (
                   self.current_position, self._number_of_pictures, self._current_laser_position
                ))
                self.current_position += 1

                if self.actor_ref.is_alive():
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

    # on stop pykka actor
    def on_stop(self):
        self._worker_pool.clear_task_queue()
        self._worker_pool.kill()
        self.hardwareController.stop_camera_stream()
        self.hardwareController.turntable.stop_turning()
        self.hardwareController.led.off()
        self.hardwareController.laser.off(0)
        self.hardwareController.laser.off(1)


    def stop_scan(self):
        self._stop_scan = True
        self._worker_pool.kill()
        self._starttime = 0
        self.utils.delete_scan(self._prefix)
        self.reset_scanner_state()
        self._logger.info("Scan stoped")
        self.hardwareController.stop_camera_stream()

        message = {
            "message": "SCAN_CANCELED",
            "level": "info"
        }
        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def image_processed(self, eventmanager, event):
        points = []

        scan_state = 'texture_scan'
        if event['image_type'] == 'depth':

            scan_state = 'object_scan'
            point_cloud = zip(event['point_cloud'][0], event['point_cloud'][1], event['point_cloud'][2],
                              event['texture'][0], event['texture'][1], event['texture'][2])

            self.append_points(point_cloud)

            for index, point in enumerate(point_cloud):
                new_point = dict()
                new_point['x'] = str(point[0])
                new_point['y'] = str(point[2])
                new_point['z'] = str(point[1])

                new_point['r'] = str(point[5])
                new_point['g'] = str(point[4])
                new_point['b'] = str(point[3])

                points.append(new_point)

        self.semaphore.acquire()
        self._progress += 1
        self.semaphore.release()

        message = {
            "points": points,
            "progress": self._progress,
            "resolution": self._total,
            "starttime": self._starttime,
            "timestamp": self.get_time_stamp(),
            "state": scan_state
        }

        self.eventmanager.broadcast_client_message(FSEvents.ON_NEW_PROGRESS, message)


        if self._progress == self._total:
            while not self.image_task_q.empty():
                #wait until the last image is processed and send to the client.
                time.sleep(0.1)

            self.scan_complete()



    def scan_complete(self):

        end_time = self.get_time_stamp()
        duration = int(end_time - self._starttime)/1000
        self._logger.debug("Time Total: %i sec." % (duration,))

        self._starttime = 0
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
        self.eventmanager.publish(FSEvents.COMMAND, event)

        message = {
            "message": "SCAN_COMPLETE",
            "scan_id": self._prefix,
            "level": "success"
        }

        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.hardwareController.stop_camera_stream()


    def append_points(self, point_cloud_set):
        if self.point_cloud:
            self.point_cloud.append_points(point_cloud_set)
            #self.point_cloud.append_texture(texture_set)

    def get_resolution(self):
        return self.settings.resolution

    def get_number_of_pictures(self):
        return self._number_of_pictures

    def get_folder_name(self):
        return self._prefix

    def reset_scanner_state(self):
        self._logger.info("Reseting scanner states ... ")
        self.hardwareController.camera.device.flush_stream()
        self.hardwareController.laser.off()
        self.hardwareController.led.off()
        self.hardwareController.turntable.disable_motors()
        self._progress = 0
        self.current_position = 0
        self._number_of_pictures = 0
        self._total = 0
        self._starttime = 0
        self.point_cloud = None

    def get_time_stamp(self):
        return int(datetime.now().strftime("%s%f"))/1000
