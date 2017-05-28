__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from Queue import Empty
import multiprocessing
import logging
import time

from fabscan.vision.FSImageTask import ImageTask, FSTaskType
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.util.FSInject import inject
from fabscan.file.FSImage import FSImage
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface


@inject(
        config=ConfigInterface,
        settings=SettingsInterface,
        imageprocessor=ImageProcessorInterface
)
class FSImageWorkerPool():
    def __init__(self, task_q, event_q, config, settings, imageprocessor):
        self._task_q = task_q
        self._event_q = event_q
        self.config = config
        self.settings = settings
        self.imageprocessor = imageprocessor
        self._logger = logging.getLogger(__name__)

        self.workers = []
        self._number_of_workers = multiprocessing.cpu_count()
        self._workers_active = False


    def create(self, number_of_workers):
        '''
            Create Processes in Pool
        '''

        self.set_number_of_workers(number_of_workers)
        self._logger.info("Creating %i image worker processes." % number_of_workers)

        for _ in range(self._number_of_workers):
            worker = FSImageWorkerProcess(self._task_q, self._event_q, self.config, self.settings, self.imageprocessor)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

        self._workers_active = True

        return self.workers

    def clear_task_queue(self):
        try:
            while not self._task_q.empty():
                self._task_q.get_nowait()
        except Empty:
            pass

    def kill(self):
            '''
                Kill Processes in Pool
            '''
            for _ in range(self._number_of_workers):
                task = ImageTask(None, None, None, task_type="KILL")
                self._task_q.put(task, True)

            self.clear_task_queue()

            for worker in self.workers:
                self.workers.remove(worker)

            self._workers_active = False


    def workers_active(self):
        return self._workers_active

    def set_number_of_workers(self, number):
        self._number_of_workers = number


class FSImageWorkerProcess(multiprocessing.Process):
    def __init__(self,image_task_q, event_q, config, settings, imageprocessor):
        super(FSImageWorkerProcess, self).__init__(group=None)
        self.image_task_q = image_task_q
        self.settings = settings
        self.config = config
        self.exit = False
        self.event_q = event_q
        self.image = FSImage()

        self.log = logging.getLogger('IMAGE_PROCESSOR THREAD')
        self.log.setLevel(logging.DEBUG)
        self.image_processor = imageprocessor
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def run(self):
        '''
            Image Process runner
        '''

        #print "process "+str(self.pid)+" started"

        #import pydevd
        #pydevd.settrace('192.168.98.104', port=12011, stdoutToServer=True, stderrToServer=True)

        while not self.exit:
            if not self.image_task_q.empty():
                #print "process "+str(self.pid)+" handle image"

                data = dict()
                try:
                    image_task = self.image_task_q.get_nowait()

                    if image_task:

                        # we got a kill pill
                        if image_task.task_type == "KILL":
                            self._logger.debug("Killed Worker Process with PID "+str(self.pid))
                            self.exit = True
                            break

                        #print "process "+str(self.pid)+" task "+str(image_task.progress)
                        if (image_task.task_type == "PROCESS_COLOR_IMAGE"):
                            self.image.save_image(image_task.image, image_task.progress, image_task.prefix, dir_name=image_task.prefix+'/color_'+image_task.raw_dir)

                            data['points'] = []
                            data['image_type'] = 'color'

                            event = dict()
                            event['event'] = "ON_IMAGE_PROCESSED"
                            event['data'] = data

                            self.event_q.put(event)

                        if (image_task.task_type == "PROCESS_DEPTH_IMAGE"):

                            angle = float(image_task.progress * 360) / float(image_task.resolution)
                            #self._logger.debug("Progress "+str(image_task.progress)+" Resolution "+str(image_task.resolution)+" angle "+str(angle))
                            self.image.save_image(image_task.image, image_task.progress, image_task.prefix, dir_name=image_task.prefix+'/laser_'+image_task.raw_dir)
                            color_image = self.image.load_image(image_task.progress, image_task.prefix, dir_name=image_task.prefix+'/color_'+image_task.raw_dir)

                            point_cloud, texture = self.image_processor.process_image(angle, image_task.image, color_image)
                            # FIXME: Only send event if points is non-empty
                            data['point_cloud'] = point_cloud
                            data['texture'] = texture
                            data['image_type'] = 'depth'
                            #data['progress'] = image_task.progress
                            #data['resolution'] = image_task.resolution

                            event = dict()
                            event['event'] = "ON_IMAGE_PROCESSED"
                            event['data'] = data

                            self.event_q.put(event)

                except Empty:
                    time.sleep(0.05)
                    pass
            else:
                # thread idle
                time.sleep(0.05)
