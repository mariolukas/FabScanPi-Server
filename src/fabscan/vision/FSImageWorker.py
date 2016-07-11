__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

from Queue import Empty
import multiprocessing
import logging
import time

from fabscan.FSConfig import Config
from fabscan.file.FSImage import save_image, load_image
from fabscan.vision.FSImageTask import ImageTask, FSTaskType
from fabscan.vision.FSImageProcessorFactory import FSImageProcessorFactory
from fabscan.FSSettings import Settings
from fabscan.FSScanner import FSEvents


class FSImageWorkerPool():
    def __init__(self, task_q, event_q):
        self._task_q = task_q
        self._event_q = event_q
        self.workers = []
        self.config = Config.instance()

        self._number_of_workers = self.config.process_numbers
        self._workers_active = False
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def create(self, number_of_workers):
        '''
            Create Processes in Pool
        '''

        self.set_number_of_workers(number_of_workers)
        self._logger.info("Creating %i image worker processes." % number_of_workers)

        for _ in range(self._number_of_workers):
            worker = FSImageWorkerProcess(Settings.instance(), Config.instance(), self._task_q, self._event_q)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

        self._workers_active = True

        return self.workers

    def kill(self):
            '''
                Kill Processes in Pool
            '''
            #print "killing "+str(self._number_of_workers)+" processes"
            i=0
            for _ in range(self._number_of_workers):

                task = ImageTask(None,None,None,task_type="KILL")
                self._task_q.put(task,True)
                i += 1

            self._workers_active = False

    def workers_active(self):
        return self._workers_active

    def set_number_of_workers(self, number):
        self._number_of_workers =  number

class FSImageWorkerProcess(multiprocessing.Process):
    def __init__(self, settings, config , image_task_q, event_q):
        super(FSImageWorkerProcess, self).__init__(group=None)
        self.image_task_q = image_task_q
        self.settings = settings
        self.config = config
        self.exit = False
        self.event_q = event_q

        self.log = logging.getLogger('IMAGE_PROCESSOR THREAD')
        self.log.setLevel(logging.DEBUG)
        self.image_processor = FSImageProcessorFactory.get_image_processor_class(self.config.scanner_type)
        #self.image_processor = ImageProcessor(self.config, self.settings)
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def run(self):
        '''
            Image Process runner
        '''

        #print "process "+str(self.pid)+" started"

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
                            save_image(image_task.image, image_task.progress, image_task.prefix, dir_name=image_task.prefix+'/color_'+image_task.raw_dir)

                            event = dict()
                            event['event'] = FSEvents.ON_IMAGE_PROCESSED
                            event['data'] = {
                                "points": [],
                                "image_type": "color"

                            }

                            self.event_q.put(event)


                        if (image_task.task_type == "PROCESS_DEPTH_IMAGE"):

                            angle = (image_task.progress) * 360 / image_task.resolution
                            save_image(image_task.image, image_task.progress, image_task.prefix, dir_name=image_task.prefix+'/laser_'+image_task.raw_dir)
                            color_image = load_image(image_task.progress, image_task.prefix, dir_name=image_task.prefix+'/color_'+image_task.raw_dir)

                            points = self.image_processor.process_image(angle, image_task.image, color_image)

                            event = dict()
                            event['event'] = FSEvents.ON_IMAGE_PROCESSED
                            event['data'] = {
                                "points" : points,
                                "image_type" : "laser"
                            }

                            self.event_q.put(event)

                except Empty:
                    time.sleep(0.05)
                    pass
            else:
                # thread idle
                time.sleep(0.05)
