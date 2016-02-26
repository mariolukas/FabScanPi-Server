__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import pykka
import time
import datetime
import multiprocessing
import subprocess
import os
import logging

from fabscan.util import FSUtil
from fabscan.file.FSPointCloud import FSPointCloud
from fabscan.vision.FSImageProcessor import ImageProcessor
from fabscan.vision.FSImageWorker import FSImageWorkerPool
from fabscan.FSEvents import FSEventManager, FSEvents, FSEvent
from fabscan.vision.FSImageTask import ImageTask, FSTaskType
from fabscan.vision.FSImageWorker import FSImageWorkerPool
from fabscan.controller import HardwareController
from fabscan.FSConfig import Config
from fabscan.FSSettings import Settings



class FSScanProcessor(pykka.ThreadingActor):

    def __init__(self):
        super(FSScanProcessor, self).__init__()

        self.eventManager = FSEventManager.instance()
        self.settings = Settings.instance()
        self.config = Config.instance()

        self._logger =  logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        self._prefix = None
        self._resolution = 16
        self._number_of_pictures = 0
        self._total = 0
        self._laser_positions = 1
        self._progress = 0
        self._is_color_scan = True
        self.point_cloud = None
        self.image_task_q = multiprocessing.Queue(self.config.process_numbers+1)
        self.current_position = 0
        self._laser_angle = 33.0
        self._stop_scan = False
        self._current_laser_position = 1

        self.semaphore = multiprocessing.BoundedSemaphore()
        self.event_q = self.eventManager.get_event_q()

        self._worker_pool = FSImageWorkerPool(self.image_task_q,self.event_q)
        self.hardwareController = HardwareController.instance()
        self.eventManager.subscribe(FSEvents.ON_IMAGE_PROCESSED, self.image_processed)
        self._scan_brightness = self.settings.camera.brightness
        self._scan_contrast = self.settings.camera.contrast
        self._scan_saturation = self.settings.camera.saturation


    def on_receive(self, event):
        if event[FSEvents.COMMAND] == 'START':
            self.start_scan()

        if event[FSEvents.COMMAND] == 'STOP':
            self.stop_scan()

        if event[FSEvents.COMMAND] == 'SCAN_NEXT_TEXTURE_POSITION':
            self.scan_next_texture_position()

        if event[FSEvents.COMMAND] == 'SCAN_NEXT_OBJECT_POSITION':
            self.scan_next_object_position()


    def start_scan(self):
        self._logger.info("Scan started")
        self._stop_scan = False
        self.hardwareController.laser.off()
        self.hardwareController.turntable.stop_turning()
        self.hardwareController.turntable.enable_motors()
        self._resolution = int(self.settings.resolution)
        self._laser_positions = int(self.settings.laser_positions)
        self._is_color_scan = bool(self.settings.color)

        self._number_of_pictures = 3200 / int(self.settings.resolution)
        self.current_position = 0

        #TODO: rename prefix to scan_id
        self._prefix = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
        self.point_cloud = FSPointCloud(self._is_color_scan)
        self.image_processor = ImageProcessor(self.config,self.settings)


        if self._is_color_scan:
            self._total = self._number_of_pictures*2*self.settings.laser_positions
            self.actor_ref.tell({FSEvents.COMMAND:'SCAN_NEXT_TEXTURE_POSITION'})
        else:
            self._total = self._number_of_pictures*self.settings.laser_positions
            self.actor_ref.tell({FSEvents.COMMAND:'SCAN_NEXT_OBJECT_POSITION'})


    def init_texture_scan(self):
        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_INFO_MESSAGE
        message['data']['message'] = "SCANNING_TEXTURE"
        message['data']['level'] = "info"
        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)
        self._worker_pool.create(self.config.process_numbers)


        self._scan_brightness = self.settings.camera.brightness
        self._scan_contrast =  self.settings.camera.contrast
        self._scan_saturation = self.settings.camera.saturation

        self.hardwareController.camera.device.textureExposure()
        self.settings.camera.brightness = 50
        self.settings.camera.contrast = 0
        self.settings.camera.saturation = 0
        self.hardwareController.led.on(60,60,60)
        time.sleep(2)
        self.hardwareController.camera.device.flushStream()
        time.sleep(1)
        self.hardwareController.camera.device.getStream()


    def finish_texture_scan(self):
        self._logger.info("Finishing texture scan.")
        self.current_position = 1
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
                self.image_task_q.put(task,True)
                self._logger.debug("Color Progress %i of %i : " % (self.current_position, self._number_of_pictures))
                self.current_position +=1
                self.actor_ref.tell({FSEvents.COMMAND:'SCAN_NEXT_TEXTURE_POSITION'})

            else:

                self.finish_texture_scan()
                self.actor_ref.tell({FSEvents.COMMAND:'SCAN_NEXT_OBJECT_POSITION'})


    def init_object_scan(self):
        self._logger.debug("Started object scan initialisation")

        self.current_position = 0

        self._laser_positions = self.settings.laser_positions
        self.hardwareController.led.on(self.settings.led.red,self.settings.led.green,self.settings.led.blue)

        self.hardwareController.laser.on()

        self.settings.camera.brightness = self._scan_brightness
        self.settings.camera.contrast = self._scan_contrast
        self.settings.camera.saturation = self._scan_saturation

        # TODO: solve this timing issue!
        # Workaround for Logitech webcam. We have to wait a loooong time until the logitech cam is ready...
        #time.sleep(3)


        self.hardwareController.camera.device.objectExposure()
        self.hardwareController.camera.device.flushStream()
        time.sleep(2)

        if self._current_laser_position == 1:
            self._laser_angle = self.image_processor.calculate_laser_angle(self.hardwareController.camera.device.getStream())
        else:
            self._laser_angle = self._laser_angle + (360/3200)
            #self._logger.debug("Calculated laser Angle is: "+str(self._laser_angle))

        if self._laser_angle == None:
            event = FSEvent()
            event.command = '_LASER_DETECTION_FAILED'
            self.eventManager.publish(FSEvents.COMMAND,event)
            self.on_laser_detection_failed()
            self._logger.debug("Send laser detection failure event")
        else:
            message = FSUtil.new_message()
            message['type'] = FSEvents.ON_INFO_MESSAGE

            message['data']['message'] = "SCANNING_OBJECT"
            message['data']['level'] = "info"
            self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)

            self._logger.debug("Detected Laser Angle at: %f deg" %(self._laser_angle, ))
            self._worker_pool.create(self.config.process_numbers)


    def finish_object_scan(self):
        self._logger.info("Finishing object scan.")
        self._worker_pool.kill()
        self.hardwareController.laser.off()
        self.hardwareController.led.off()
        self.hardwareController.camera.device.setPreviewResolution()


    def scan_next_object_position(self):
        if not self._stop_scan:
            if self.current_position < self._number_of_pictures:
                if self.current_position == 0:
                    self.init_object_scan()

                laser_image = self.hardwareController.scan_at_position(self._resolution)
                task = ImageTask(laser_image, self._prefix, self.current_position, self._number_of_pictures)
                self.image_task_q.put(task)
                self._logger.debug("Laser Progress: %i of %i at laser position %i" %(self.current_position, self._number_of_pictures  , self._current_laser_position))
                self.current_position +=1
                self.actor_ref.tell({FSEvents.COMMAND:'SCAN_NEXT_OBJECT_POSITION'})

            elif self._current_laser_position <= self.settings.laser_positions:
                self.current_position = 0
                self._current_laser_position +=1;
                self.hardwareController.laser.step(-1, 100)
                self.scan_next_object_position()

            else:
                self._logger.debug("End of scan_next_object reached.")
                self.finish_object_scan()


    def on_laser_detection_failed(self):

        self._logger.info("Send laser detection failed message to frontend")
        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_INFO_MESSAGE
        message['data']['message'] = "NO_LASER_FOUND"
        message['data']['level'] = "warn"
        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)


    def stop_scan(self):

       self._stop_scan = True
       self._worker_pool.kill()
       time.sleep(1)
       FSUtil.delete_scan(self._prefix)
       self.reset_scanner_state()
       self._logger.info("Scan stoped")


    def on_stop(self):

        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_INFO_MESSAGE
        message['data']['message'] = "SCAN_CANCELED"
        message['data']['level'] = "info"
        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)
        #self.eventManager.unsubscribe(FSEvents.ON_IMAGE_PROCESSED, self.image_processed)


    def image_processed(self, eventManager, event):

        if event['image_type'] == 'laser':
            self.append_points(event['points'])

        self.semaphore.acquire()
        self._progress +=1
        self.semaphore.release()

        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_NEW_PROGRESS
        message['data']['points'] = event['points']
        message['data']['progress'] = self._progress
        message['data']['resolution'] = self._total

        if self._progress == self._total:
                self.scan_complete()

        eventManager.publish(FSEvents.ON_SOCKET_BROADCAST, message)


    def scan_complete(self):



        self._logger.debug("Scan complete writing pointcloud files with %i points." % (self.point_cloud.get_size(),))
        self.point_cloud.saveAsFile(self._prefix)
        self.settings.saveAsFile(self._prefix)
        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_INFO_MESSAGE
        message['data']['message'] = "SAVING_POINT_CLOUD"
        message['data']['scan_id'] = self._prefix
        message['data']['level'] = "info"
        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)


        FSUtil.delete_image_folders(self._prefix)
        self.reset_scanner_state()

        event = FSEvent()
        event.command = '_COMPLETE'
        #TODO: generate MESH Here!
        self.eventManager.publish(FSEvents.COMMAND,event)

        message = FSUtil.new_message()
        message['type'] = FSEvents.ON_INFO_MESSAGE
        message['data']['message'] = "SCAN_COMPLETE"
        message['data']['scan_id'] = self._prefix
        message['data']['level'] = "success"

        self.eventManager.publish(FSEvents.ON_SOCKET_BROADCAST,message)



    def create_mesh(self, prefix):

        basedir = os.path.dirname(os.path.dirname(__file__))
        input =  self.config.folders.scans+str(prefix)+"/"+str(prefix)+".ply"
        output = self.config.folders.scans+str(prefix)+"/"+str(prefix)+".stl"
        mlx = basedir+"/fabscan/static/data/mlx/default_mesh.mlx"
        os.environ["DISPLAY"]=":0"
        subprocess.call([self.config.meshlab.path+"/meshlabserver -i "+input+" -o "+output+" -s "+mlx],shell=True)
        self._logger.debug("STL File written.")



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
        if self.settings.laser_positions > 1:
            self.hardwareController.laser.step(self.settings.laser_positions, 100)
        self.hardwareController.camera.device.objectExposure()
        self.hardwareController.camera.device.flushStream()
        self.hardwareController.laser.off()
        self.hardwareController.led.off()
        self.hardwareController.turntable.disable_motors()
        self._command = None
        self._progress = 0
        self.current_position = 0
        self._number_of_pictures = 0
        self._total = 0
        self._current_laser_position = 0
