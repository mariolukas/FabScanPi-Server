__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import cv2
import time
import logging
import threading
from datetime import datetime


from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface

from fabscan.lib.util.FSUtil import FSSystem
from fabscan.lib.file.FSPointCloud import FSPointCloud
from fabscan.FSEvents import FSEventManagerSingleton, FSEvents, FSEvent
from fabscan.worker.FSImageTask import ImageTask
from fabscan.lib.util.FSInject import inject, singleton

from fabscan.scanner.interfaces.FSHardwareController import FSHardwareControllerInterface
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorInterface
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from fabscan.scanner.interfaces.FSScanProcessor import FSScanProcessorCommand
from fabscan.scanner.interfaces.FSCalibration import FSCalibrationInterface
from fabscan.worker.FSImageWorker import FSImageWorkerPool, FSSWorkerPoolCommand

import asyncio

@inject(
    config=ConfigInterface,
    settings=SettingsInterface,
    eventmanager=FSEventManagerSingleton,
    imageprocessor=ImageProcessorInterface,
    hardwarecontroller=FSHardwareControllerInterface,
    calibration=FSCalibrationInterface,
)
class FSScanProcessor(FSScanProcessorInterface):
    def __init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller, calibration):
        super(FSScanProcessorInterface, self).__init__(self, config, settings, eventmanager, imageprocessor, hardwarecontroller, calibration)

        #asyncio.set_event_loop(asyncio.new_event_loop())
        self.settings = settings
        self.config = config
        self._logger = logging.getLogger(__name__)

        self.eventmanager = eventmanager.instance
        self.calibration = calibration
        self._worker_pool = None
        self.hardwareController = hardwarecontroller
        self.image_processor = imageprocessor

        self._prefix = None
        self._resolution = 16
        self._number_of_pictures = 0
        self._total = 1
        self._progress = 1
        self._is_color_scan = True
        self.point_clouds = []
        self.both_cloud = []

        self.current_position = 0
        self._stop_scan = False
        self._current_laser_position = 1
        self._starttime = 0
        self._additional_worker_number = 1

        self.texture_lock_event = threading.Event()
        self.texture_lock_event.set()

        self.utils = FSSystem()

        self._scan_brightness = self.settings.file.camera.brightness
        self._scan_contrast = self.settings.file.camera.contrast
        self._scan_saturation = self.settings.file.camera.saturation
        self._logger.info("Laser Scan Processor initilized.")

        # prevent deadlocks when opencv tbb is not available

        cv_build_info = cv2.getBuildInformation()

        # fallback to one worker.
        if not "TBB" in cv_build_info:
            self._logger.warning("OpenCV does not support TBB. Falling back to single processing.")
            self.config.file.process_numbers = 1

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

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.GET_SETTINGS_STREAM:
            return self.create_settings_stream()

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

        if event[FSEvents.COMMAND] == FSScanProcessorCommand.IMAGE_PROCESSED:
            self.image_processed(event['RESULT'])

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

    def scanner_is_calibrated(self):
        correct_plane_number = len(self.config.file.calibration.laser_planes) == self.config.file.laser.numbers

        distance_is_set = True
        for i in range(self.config.file.laser.numbers - 1):
            plane = self.config.file.calibration.laser_planes[i]
            if (plane['distance'] is None) or (plane['distance'] == 0):
                distance_is_set = False
                break

        is_calibrated = correct_plane_number and distance_is_set
        return is_calibrated

    def notify_if_is_not_calibrated(self):
        try:
            self._logger.debug(self.config.file.calibration.camera_matrix)

            is_calibrated = self.scanner_is_calibrated()
            self._logger.debug("FabScan is calibrated: {0}".format(is_calibrated))

            if not is_calibrated:
                message = {
                    "message": "SCANNER_NOT_CALIBRATED",
                    "level": "warn"
                }

                self._logger.debug("Clients informaed")

                event = FSEvent()
                event.command = "STOP"
                self.eventmanager.publish(FSEvents.COMMAND, event)
                self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

            return

        except Exception as e:
            self._logger.exception(e)

    def create_texture_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self.image_processor.get_texture_stream_frame(image)
            return image
        except Exception as e:
            #self._logger.error(e)
            pass

    def create_settings_stream(self):
        try:
            image = self.hardwareController.get_picture()
            image = self.image_processor.get_laser_stream_frame(image)
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
            image = self.image_processor.get_laser_stream_frame(image)
            return image
        except Exception as e:
            #self._logger.error("Error while grabbing laser Frame: " + str(e))
            # images are dropped this cateched exception.. no error hanlder needed here.
            pass


    def update_settings(self, settings):
        try:
            self.settings.update(settings)
            #FIXME: Only change Color Settings when values changed.
            self.hardwareController.led.on(self.settings.file.led.red, self.settings.file.led.green, self.settings.file.led.blue)
        except Exception as e:
            self._logger.exception("Updating Settings failed: {0}".format(e))
            pass

    def update_config(self, config):
        try:
            self.config.file.update(config)
        except Exception as e:
            pass

    def start_calibration(self):
        self.hardwareController.settings_mode_off()
        self.calibration.start()

    def stop_calibration(self):
        self.calibration.stop()

    def send_hardware_state_notification(self):
        self._logger.debug("Checking Hardware connections")

        if not self.hardwareController.hardware_connector_available():
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

    ## general start sequence

    def start_scan(self):
        self.settings_mode_off()
        self._logger.info("Scan started")
        self._stop_scan = False

        self.hardwareController.turntable.enable_motors()
        for i in range(int(self.config.file.laser.numbers)):
            self.hardwareController.laser.off(i)

        self._resolution = int(self.settings.file.resolution)
        self._is_color_scan = bool(self.settings.file.color)
        self._number_of_pictures = int(self.config.file.turntable.steps // self._resolution)

        self.current_position = 0
        self._starttime = self.get_time_stamp()

        # TODO: rename prefix to scan_id
        self._prefix = datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')

        # initialize pointcloud actors...
        self.point_clouds = []
        #self.point_clouds = [FSPointCloud(config=self.config, color=self._is_color_scan) for _ in range(self.config.file.laser.numbers)]

        for laser_index in range(self.config.file.laser.numbers):
            self.point_clouds.append(FSPointCloud(config=self.config, color=self._is_color_scan, filename=self._prefix, postfix=laser_index, binary=False))

        if self.config.file.laser.numbers > 1:
            self.both_cloud = FSPointCloud(config=self.config, color=self._is_color_scan, filename=self._prefix, postfix='both', binary=False)

        if self.scanner_is_calibrated() and self.actor_ref.is_alive():
            if self._is_color_scan:
                self._total = (self._number_of_pictures * self.config.file.laser.numbers) + self._number_of_pictures
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_TEXTURE_POSITION})
            else:
                self._total = self._number_of_pictures * self.config.file.laser.numbers
                self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION})
        else:
            self._logger.debug("FabScan is not calibrated scan canceled")
            self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand.NOTIFY_IF_NOT_CALIBRATED})


    ## texture callbacks
    def init_texture_scan(self):
        message = {
            "message": "SCANNING_TEXTURE",
            "level": "info"
        }
        if self._worker_pool is None or not self._worker_pool.is_alive():
            self._worker_pool = FSImageWorkerPool.start(scanprocessor=self.actor_ref)

        if self._worker_pool.is_alive():
            self._logger.debug("Adding some workers to Pool.")
            self._worker_pool.tell(
                {FSEvents.COMMAND: FSSWorkerPoolCommand.CREATE, 'NUMBER_OF_WORKERS': self._additional_worker_number}
            )

        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

        self._scan_brightness = self.settings.file.camera.brightness
        self._scan_contrast = self.settings.file.camera.contrast
        self._scan_saturation = self.settings.file.camera.saturation
        self.hardwareController.led.on(self.config.file.texture_illumination, self.config.file.texture_illumination, self.config.file.texture_illumination)
        self.hardwareController.start_camera_stream(mode="default")
        # wait until camera is settled
        time.sleep(1)
        self.hardwareController.camera.device.flush_stream()



    def scan_next_texture_position(self):
        if not self._stop_scan:

            try:
                if self.current_position < self._number_of_pictures and self.actor_ref.is_alive():

                    flush = False

                    if self.current_position == 0:
                        flush = True
                        self.init_texture_scan()

                    color_image = self.hardwareController.get_picture(flush=flush)
                    color_image = self.image_processor.decode_image(color_image)
                    self.hardwareController.move_to_next_position(steps=self._resolution, speed=800)

                    task = ImageTask(color_image, self._prefix, self.current_position, self._number_of_pictures, task_type="PROCESS_COLOR_IMAGE")

                    self._worker_pool.tell(
                        {FSEvents.COMMAND: FSSWorkerPoolCommand.ADD_TASK, 'TASK': task}
                    )
                    color_image = None
                    self.current_position += 1

                    if self.actor_ref.is_alive():
                        time.sleep(0.1)
                        #self.self.texture_lock_event.clear()
                        self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_TEXTURE_POSITION})

                    else:
                        self._logger.error("Worker Pool died.")
                        self.stop_scan()
                else:
                   self.finish_texture_scan()
                   if self.actor_ref.is_alive():
                      self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION})
                   else:
                      self._logger.error("Worker Pool died.")
                      self.stop_scan()
            except Exception as e:
                self._logger.exception("Scan Processor Error: {0}".format(e))

    def finish_texture_scan(self):
        self._logger.info("Finishing texture scan.")
        self.current_position = 0

        self.hardwareController.led.off()

        self.settings.file.camera.brightness = self._scan_brightness
        self.settings.file.camera.contrast = self._scan_contrast
        self.settings.file.camera.saturation = self._scan_saturation

    ## object scan callbacks
    def init_object_scan(self):
        self.hardwareController.start_camera_stream()
        if self._worker_pool is None or not self._worker_pool.is_alive():
            self._worker_pool = FSImageWorkerPool.start(scanprocessor=self.actor_ref)
        self._logger.info("Started object scan initialisation")
        if self._is_color_scan:
            self._additional_worker_number = 3
        else:
            self._additional_worker_number = 4

        self._logger.debug("Adding some workers to pool.")
        self._worker_pool.tell(
            {FSEvents.COMMAND: FSSWorkerPoolCommand.CREATE, 'NUMBER_OF_WORKERS': self._additional_worker_number}
        )

        message = {
            "message": "SCANNING_OBJECT",
            "level": "info"
        }
        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.current_position = 0

        if self.config.file.laser.interleaved == "False":
            self.hardwareController.led.off()

        self.hardwareController.camera.flush_stream()

    def scan_next_object_position(self):
        if not self._stop_scan:
            if self.current_position <= self._number_of_pictures and self.actor_ref.is_alive():
                if self.current_position == 0:
                    self.init_object_scan()

                self._logger.debug('Start creating Task.')
                for laser_index in range(self.config.file.laser.numbers):
                    laser_image = self.hardwareController.get_image_at_position(index=laser_index)
                    task = ImageTask(laser_image, self._prefix, self.current_position, self._number_of_pictures, index=laser_index)

                    self._worker_pool.tell(
                        {FSEvents.COMMAND: FSSWorkerPoolCommand.ADD_TASK, 'TASK': task}
                    )

                self.current_position += 1
                self.hardwareController.move_to_next_position(steps=self._resolution, speed=800)
                self._logger.debug('New Image Task created.')

                if self.actor_ref.is_alive():
                    self.actor_ref.tell({FSEvents.COMMAND: FSScanProcessorCommand._SCAN_NEXT_OBJECT_POSITION})
                else:
                    self._logger.error("Worker Pool died.")
                    self.stop_scan()

                self._logger.debug('End creating Task.')


    def on_laser_detection_failed(self):

        self._logger.info("Send laser detection failed message to frontend")
        message = {
            "message": "NO_LASER_FOUND",
            "level": "warn"
        }

        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.settings_mode_on()

    # pykka actor stop event
    def on_stop(self):
        self.stop_scan()

        self.hardwareController.destroy_camera_device()
        self.finishFiles()

        self.hardwareController.turntable.stop_turning()
        self.hardwareController.led.off()
        for laser_index in range(self.config.file.laser.numbers):
            self.hardwareController.laser.off(laser_index)

    # on stop command by user
    def stop_scan(self):
        self._stop_scan = True

        self._starttime = 0
        self.finishFiles()

        if self._prefix:
            self.utils.delete_folder(str(self.config.file.folders.scans)+'/'+str(self._prefix))

        self.reset_scanner_state()
        self._logger.info("Scan stoped")
        self.hardwareController.stop_camera_stream()

        message = {
            "message": "SCAN_CANCELED",
            "level": "info"
        }
        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)

    def clear_and_stop_worker_pool(self):
        # clear queue
        if self._worker_pool and self._worker_pool.is_alive():
            self._logger.debug("Stopping worker Pool.")
            self._worker_pool.stop()

    def image_processed(self, result):
        if not self._stop_scan:
            if self._progress <= self._total and self.actor_ref.is_alive():
                points = []

                if not 'laser_index' in list(result.keys()):
                    result['laser_index'] = -1

                try:
                    scan_state = 'texture_scan'
                    if result['image_type'] == 'depth' and result['point_cloud'] is not None:
                        scan_state = 'object_scan'

                        point_cloud = zip(result['point_cloud'][0], result['point_cloud'][1], result['point_cloud'][2],
                                          result['texture'][0], result['texture'][1], result['texture'][2])

                        for x, y, z, b, g, r in point_cloud:

                            new_point = {"x": str(x), "y": str(z), "z": str(y), "r": str(r), "g": str(g), "b": str(b)}
                            points.append(new_point)

                            self.append_points((x, y, z, r, g, b,), result['laser_index'])

                       # result = None

                except Exception as err:
                    self._logger.warning("Image processing Failure: {0}".format(err))


                message = {
                    "laser_index": result['laser_index'],
                    "points": points,
                    "progress": self._progress,
                    "resolution": self._total,
                    "starttime": self._starttime,
                    "timestamp": self.get_time_stamp(),
                    "state": scan_state
                }

                self.eventmanager.broadcast_client_message(FSEvents.ON_NEW_PROGRESS, message)

                message = None
                result = None

                self._logger.debug("Step {0} of {1}".format(self._progress, self._total))

                self._progress += 1

                if self._progress-1 == self._total:
                    self.scan_complete()


    def scan_complete(self):

        self._worker_pool.tell(
            {FSEvents.COMMAND: FSSWorkerPoolCommand.KILL}
        )

        end_time = self.get_time_stamp()
        duration = int((end_time - self._starttime)//1000)
        self._logger.debug("Time Total: {0} sec.".format(duration))

        if len(self.point_clouds) == self.config.file.laser.numbers:

            self._logger.info("Scan complete writing pointcloud.")
            self._logger.debug("Number of PointClouds (for each laser one): {0}".format(len(self.point_clouds)))

            self.finishFiles()

            settings_filename = self.config.file.folders.scans+self._prefix+"/"+self._prefix+".fab"
            self.settings.save_json(settings_filename)


        #if bool(self.config.file.keep_raw_images):
        #    self.utils.zipdir(str(self._prefix))

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
        if len(self.point_clouds) > 1:
            self.both_cloud.append_points(points)

    def finishFiles(self):

        try:
            for laser_index in range(self.config.file.laser.numbers):
                if self.point_clouds and len(self.point_clouds) > 0 and self.point_clouds[laser_index]:
                    self.point_clouds[laser_index].closeFile()
                    self.point_clouds[laser_index] = None

            if self.config.file.laser.numbers > 1:
                if self.both_cloud:
                    self.both_cloud.closeFile()
                    self.both_cloud = None

        except IOError as e:
            #TODO: Call stop scan function if this fails to release the scan process
            self._logger.exception("Closing PointCloud files failed: {0}".format(e))
            #self.scan_failed()


    def scan_failed(self):
        message = {
            "message": "SCAN_FAILED_STOPPING",
            "scan_id": self._prefix,
            "level": "error"
        }

        self.eventmanager.broadcast_client_message(FSEvents.ON_INFO_MESSAGE, message)
        self.stop_scan()

    def get_resolution(self):
        return self._resolution

    def get_number_of_pictures(self):
        return self._number_of_pictures

    def get_folder_name(self):
        return self._prefix

    def reset_scanner_state(self):
        self._logger.info("Reseting scanner states ... ")

        self.hardwareController.stop_camera_stream()
        for i in range(self.config.file.laser.numbers):
            self.hardwareController.laser.off(i)

        self.hardwareController.led.off()
        self.hardwareController.turntable.disable_motors()

        self.clear_and_stop_worker_pool()

        self._progress = 1
        self.current_position = 0
        self._number_of_pictures = 0
        self._total = 0
        self._starttime = 0


    def get_time_stamp(self):
        return int(datetime.now().strftime("%s%f"))/1000
