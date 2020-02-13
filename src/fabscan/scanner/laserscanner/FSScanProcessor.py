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

import asyncio

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

        asyncio.set_event_loop(asyncio.new_event_loop())
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
        self._progress = 0
        self._is_color_scan = True
        self.point_clouds = []
        self.image_task_q = multiprocessing.Queue(self.config.file.process_numbers*2)
        self.current_position = 0
        self._stop_scan = False
        self._current_laser_position = 1
        self._starttime = 0

        self.utils = FSSystem()

        self.semaphore = multiprocessing.BoundedSemaphore()
        self.event_q = self.eventmanager.get_event_q()

        self._worker_pool = None

        self._scan_brightness = self.settings.file.camera.brightness
        self._scan_contrast = self.settings.file.camera.contrast
        self._scan_saturation = self.settings.file.camera.saturation

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

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.CONFIG_MODE_ON:
            self.config_mode_on()

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.CONFIG_MODE_OFF:
            self.config_mode_off()


    def config_mode_on(self):
        self.hardwareController.start_camera_stream('alignment')

    def config_mode_off(self):
        self.hardwareController.stop_camera_stream()

        for i in range(self.config.file.laser.numbers):
            self.hardwareController.laser.off(i)

        self.hardwareController.led.off()
        self.hardwareController.turntable.stop_turning()

    def call_hardware_test_function(self, function):
        self.hardwareController.call_test_function(function)

    def notify_if_is_not_calibrated(self):
        self._logger.debug(self.config.file.calibration.camera_matrix)
        correct_plane_number = len(self.config.file.calibration.laser_planes) == self.config.file.laser.numbers

        distance_is_set = True
        for i in range(self.config.file.laser.numbers-1):
            if (self.config.file.calibration.laser_planes[i].distance == 0) or \
               (self.config.file.calibration.laser_planes[i].distance is None):
                distance_is_set = False
                break

        is_calibrated = correct_plane_number and distance_is_set

        self._logger.debug("FabScan is calibrated: " + str(is_calibrated))

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
        except Exception as e:
            #self._logger.error(e)
            pass

    def create_adjustment_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self.image_processor.get_adjustment_stream_frame(image)
            return image
        except Exception as e:
            pass

    def create_calibration_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self.image_processor.get_calibration_stream_frame(image)
            return image
        except Exception as e:
            # images are dropped this cateched exception.. no error hanlder needed here.
            pass

    def create_laser_stream(self):
        try:
            image = self.hardwareController.get_picture()

            return image
        except Exception as e:
            self._logger.error("Error while grabbing laser Frame: " + str(e))
            # images are dropped this cateched exception.. no error hanlder needed here.
            pass


    def update_settings(self, settings):
        try:
            self.settings.update(settings)
            #FIXME: Only change Color Settings when values changed.
            self.hardwareController.led.on(self.settings.file.led.red, self.settings.file.led.green, self.settings.file.led.blue)
        except Exception as e:
            self._logger.error('Updating Settings failed: ' + str(e))
            pass

    def update_config(self, config):
        try:
            self.config.file.update(config)
        except Exception as e:
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
        self.hardwareController.laser.on(0)
        self.hardwareController.start_camera_stream(mode="default")
        self._resolution = int(self.settings.file.resolution)
        self._is_color_scan = bool(self.settings.file.color)
        self.hardwareController.laser.on(1)
        self._number_of_pictures = int(self.config.file.turntable.steps // self.settings.file.resolution)
        self.current_position = 0
        self._starttime = self.get_time_stamp()

        # TODO: rename prefix to scan_id
        self._prefix = datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')

        self.point_clouds = [FSPointCloud(config=self.config, color=self._is_color_scan) for _ in range(self.config.file.laser.numbers)]

        if not (self.config.file.calibration.laser_planes[0]['normal'] == []) and self.actor_ref.is_alive():
            if self._is_color_scan:
                self._total = (self._number_of_pictures * self.config.file.laser.numbers) + self._number_of_pictures
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_TEXTURE_POSITION})
            else:
                self._total = self._number_of_pictures * self.config.file.laser.numbers
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
        self._worker_pool.create(self.config.file.process_numbers)

        self._scan_brightness = self.settings.file.camera.brightness
        self._scan_contrast = self.settings.file.camera.contrast
        self._scan_saturation = self.settings.file.camera.saturation
        self.hardwareController.led.on(self.config.file.texture_illumination, self.config.file.texture_illumination, self.config.file.texture_illumination)



    def finish_texture_scan(self):
        self._logger.info("Finishing texture scan.")
        self.current_position = 0

        self.hardwareController.led.off()

        self.settings.file.camera.brightness = self._scan_brightness
        self.settings.file.camera.contrast = self._scan_contrast
        self.settings.file.camera.saturation = self._scan_saturation

    def scan_next_texture_position(self):
        if not self._stop_scan:
            if self.current_position <= self._number_of_pictures and self.actor_ref.is_alive():

                flush = False

                if self.current_position == 0:
                    flush = True
                    self.init_texture_scan()


                color_image = self.hardwareController.get_picture(flush=flush)
                self.hardwareController.move_to_next_position(steps=self._resolution, color=True)

                task = ImageTask(color_image, self._prefix, self.current_position, self._number_of_pictures, task_type="PROCESS_COLOR_IMAGE")
                self.image_task_q.put(task, True)
                self._logger.debug("Color Progress %i of %i : " % (self.current_position, self._number_of_pictures))
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
        # wait for ending of texture stream

        if self.config.file.laser.interleaved == "False":
            self.hardwareController.laser.on()
            self.hardwareController.led.on(self.settings.file.led.red, self.settings.file.led.green, self.settings.file.led.blue)

        self.hardwareController.camera.device.flush_stream()
        #self.hardwareController.camera.device.camera.awb_mode = 'auto'

        if not self._worker_pool.workers_active():
            self._worker_pool.create(self.config.file.process_numbers)

    def finish_object_scan(self):
        self._logger.info("Finishing object scan.")
        self._worker_pool.kill()

    def scan_next_object_position(self):
        if not self._stop_scan:
            if self.current_position < self._number_of_pictures and self.actor_ref.is_alive():
                if self.current_position == 0:
                    self.init_object_scan()

                for laser_index in range(self.config.file.laser.numbers):
                    laser_image = self.hardwareController.get_image_at_position(index=laser_index)
                    task = ImageTask(laser_image, self._prefix, self.current_position, self._number_of_pictures, index=laser_index)
                    self.image_task_q.put(task)


                    self._logger.debug("Laser Progress: %i of %i at laser position %i" % (
                       self.current_position, self._number_of_pictures, self._current_laser_position
                    ))

                self.current_position += 1
                #self.hardwareController.turntable.step_blocking(self._resolution, speed=900)
                self.hardwareController.move_to_next_position(self._resolution)


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
        if self._worker_pool:
            self._worker_pool.clear_task_queue()
            self._worker_pool.kill()
        self.hardwareController.destroy_camera_device()

        self.hardwareController.turntable.stop_turning()
        self.hardwareController.led.off()
        for laser_index in range(self.config.file.laser.numbers):
            self.hardwareController.laser.off(laser_index)

    def stop_scan(self):
        self._stop_scan = True
        self._worker_pool.kill()
        self._starttime = 0
        #self.utils.delete_scan(self._prefix)
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

        if not 'laser_index' in list(event.keys()):
            event['laser_index'] = -1

        try:
            scan_state = 'texture_scan'
            if event['image_type'] == 'depth' and event['point_cloud'] is not None:
                scan_state = 'object_scan'
                point_cloud = list(zip(event['point_cloud'][0], event['point_cloud'][1], event['point_cloud'][2],
                                  event['texture'][0], event['texture'][1], event['texture'][2]))

                self.append_points(point_cloud, event['laser_index'])

                for index, point in enumerate(point_cloud):
                    new_point = dict()
                    new_point['x'] = str(point[0])
                    new_point['y'] = str(point[2])
                    new_point['z'] = str(point[1])

                    new_point['r'] = str(point[5])
                    new_point['g'] = str(point[4])
                    new_point['b'] = str(point[3])

                    points.append(new_point)
        except Exception as err:
            self._logger.error('Image processing Error:' + str(err))

        #self.semaphore.acquire()
        self._progress += 1
        #self.semaphore.release()

        message = {
            "laser_index": event['laser_index'],
            "points": points,
            "progress": self._progress,
            "resolution": self._total,
            "starttime": self._starttime,
            "timestamp": self.get_time_stamp(),
            "state": scan_state
        }

        self._logger.debug(str(self._progress) + " von " + str(self._total))
        self.eventmanager.broadcast_client_message(FSEvents.ON_NEW_PROGRESS, message)


        if self._progress >= self._total:
            while not self.image_task_q.empty():
                #wait until the last image is processed and send to the client.
                time.sleep(0.1)

            self.scan_complete()


    def scan_complete(self):

        end_time = self.get_time_stamp()
        duration = int((end_time - self._starttime)//1000)
        self._logger.debug("Time Total: %i sec." % (duration,))

        self._starttime = 0

        if len(self.point_clouds) == self.config.file.laser.numbers:

            self._logger.info("Scan complete writing pointcloud.")

            if self.config.file.laser.numbers > 1:
                both_cloud = FSPointCloud(color=self._is_color_scan)

            self._logger.debug('Number of PointClouds (for each laser one) : ' +str(len(self.point_clouds)))

            for laser_index in range(self.config.file.laser.numbers):
                points = self.point_clouds[laser_index].get_points()
                if self.config.file.laser.numbers > 1:
                    both_cloud.append_points(points)
                self.point_clouds[laser_index].saveAsFile(self._prefix,  str(laser_index))

            if self.config.file.laser.numbers > 1:
                both_cloud.saveAsFile(self._prefix, 'both')

            settings_filename = self.config.file.folders.scans+self._prefix+"/"+self._prefix+".fab"
            self.settings.save_json(settings_filename)

            message = {
                "message": "SAVING_POINT_CLOUD",
                "scan_id": self._prefix,
                "level": "info"
            }

            self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        if bool(self.config.file.keep_raw_images):
            self.utils.zipdir(str(self._prefix))

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


    def append_points(self, points, index):
        if len(self.point_clouds) > 0:
            self.point_clouds[index].append_points(points)
            #self.point_cloud.append_texture(texture_set)

    def get_resolution(self):
        return self.settings.file.resolution

    def get_number_of_pictures(self):
        return self._number_of_pictures

    def get_folder_name(self):
        return self._prefix

    def reset_scanner_state(self):
        self._logger.info("Reseting scanner states ... ")
        self.hardwareController.camera.device.flush_stream()

        for i in range(self.config.file.laser.numbers):
            self.hardwareController.laser.off()

        self.hardwareController.led.off()
        self.hardwareController.turntable.disable_motors()
        self._progress = 0
        self.current_position = 0
        self._number_of_pictures = 0
        self._total = 0
        self._starttime = 0

        self.point_clouds = []

    def get_time_stamp(self):
        return int(datetime.now().strftime("%s%f"))/1000
