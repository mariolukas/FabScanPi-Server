__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import linecache
import os

from queue import Empty
import multiprocessing
import logging
import time
import numpy as np

from fabscan.worker.FSImageTask import ImageTask, FSTaskType
from fabscan.scanner.interfaces.FSScanActor import FSScanActorCommand, FSScanActorInterface
from fabscan.FSConfig import ConfigInterface
from fabscan.FSSettings import SettingsInterface
from fabscan.lib.util.FSInject import inject
from fabscan.lib.file.FSImage import FSImage
from fabscan.scanner.interfaces.FSImageProcessor import ImageProcessorInterface
from pykka import ThreadingActor
from fabscan.FSEvents import FSEvents


class FSSWorkerPoolCommand(object):
    CREATE = "CREATE"
    KILL = "KILL"
    CLEAR_QUEUE = "CLEAR_QUEUE"
    ADD_TASK = "ADD_TASK"
    IS_ACTIVE = "IS_ACTIVE"
    HANLDE_OUTPUT = "HANLDE_OUTPUT"

@inject(
        config=ConfigInterface,
        settings=SettingsInterface
)
class FSImageWorkerPool(ThreadingActor):

    def __init__(self, config, settings, scanActor):
        super(FSImageWorkerPool, self).__init__(self, config, settings, scanActor)
        self._logger = logging.getLogger(__name__)
        self.input_muted = False
        self.scanActor = scanActor
        self.config = config
        self.settings = settings

        self._task_q = multiprocessing.Queue(self.config.file.process_numbers)
        self._output_q = multiprocessing.Queue(self.config.file.process_numbers)

        self._input_count = 0
        self._output_count = 0

        self.workers = []
        self._number_of_workers = 0
        self._workers_active = False
        self._logger.info("Worker Pool Actor initilized")

    def on_stop(self):
        if len(self.workers) > 0:
            self.kill()

    def on_receive(self, event):
        if event[FSEvents.COMMAND] == FSSWorkerPoolCommand.CREATE:
            self.create(event['NUMBER_OF_WORKERS'])
        if event[FSEvents.COMMAND] == FSSWorkerPoolCommand.KILL:
            self.kill()
        if event[FSEvents.COMMAND] == FSSWorkerPoolCommand.CLEAR_QUEUE:
            self.clear_task_queue()
        if event[FSEvents.COMMAND] == FSSWorkerPoolCommand.ADD_TASK:
            self.handle_input(event['TASK'])
        if event[FSEvents.COMMAND] == FSSWorkerPoolCommand.HANLDE_OUTPUT:
            self.handle_output()
        if event[FSEvents.COMMAND] == FSSWorkerPoolCommand.IS_ACTIVE:
            return self.workers_active()

    def handle_input(self, task):

        if self.actor_ref.is_alive() and not self.input_muted:
            self._task_q.put(task)
            self._input_count += 1

            self.actor_ref.tell(
                {FSEvents.COMMAND: FSSWorkerPoolCommand.HANLDE_OUTPUT}
            )


    def handle_output(self):
        if self._input_count > 0:
            self._input_count -= 1
            if self.scanActor.is_alive():
                self.scanActor.tell(
                    {FSEvents.COMMAND: FSScanActorCommand.IMAGE_PROCESSED, 'RESULT': self._output_q.get()}
                )

            if self.actor_ref.is_alive():
                self.actor_ref.tell(
                    {FSEvents.COMMAND: FSSWorkerPoolCommand.HANLDE_OUTPUT}
                )

    def create(self, number_of_workers):
        '''
            Create Processes in Pool
        '''

        self.set_number_of_workers(number_of_workers)
        self._logger.info("Creating {} image worker processes.".format(number_of_workers))

        for _ in range(number_of_workers):
            worker = FSImageWorkerProcess(image_task_q=self._task_q, output_q=self._output_q, config=self.config, settings=self.settings, scanActor=self.scanActor)
            #worker.daemon = True
            worker.start()
            self.workers.append(worker)

        self._workers_active = True
        return self.workers

    def clear_queue(self, q):
        while not q.empty():
            try:
                q.get_nowait()
            except Empty:
                pass

    def clear_task_queue(self):
        try:

            self.clear_queue(self._task_q)
            self.clear_queue(self._output_q)

            self._output_count = 0
            self._input_count = 0
        except Empty:
            pass

    def kill(self):
            '''
                Kill Processes in Pool
            '''
            self.input_muted = True
            self.clear_task_queue()

            for worker in self.workers:
                task = ImageTask(None, None, None, task_type="KILL")
                self._task_q.put(task, True)

            for worker in self.workers:
                self.workers.remove(worker)
                worker.join()

            self._workers_active = False
            self.input_muted = False


    def workers_active(self):
        return self._workers_active

    def set_number_of_workers(self, number):
        self._number_of_workers += number

@inject (
    imageprocessor=ImageProcessorInterface,
)
class FSImageWorkerProcess(multiprocessing.Process):
    def __init__(self, image_task_q, output_q, config, settings, scanActor, imageprocessor):
        super(FSImageWorkerProcess, self).__init__(group=None)

        self.image_task_q = image_task_q
        self.output_q = output_q
        self.settings = settings
        self.config = config
        self.exit = False
        self.scanActor = scanActor
        self.image = FSImage()

        self.log = logging.getLogger('IMAGE_PROCESSOR THREAD')
        self.log.setLevel(logging.DEBUG)
        self.image_processor = imageprocessor
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def kill(self):
        self.exit = True

    def run(self):
        '''
            Image Process runner
        '''

        self._logger.debug("process {} started".format(self.pid))


        while not self.exit:

            if not self.image_task_q.empty():

                try:
                    image_task = self.image_task_q.get_nowait()

                    if image_task:

                        data = dict()
                        if image_task.task_type == "KILL":
                            self.exit = True
                            break

                        if (image_task.task_type == "PROCESS_COLOR_IMAGE"):

                            #image = self.image_processor.decode_image(image_task.image)
                            self.image.save_image(image_task.image, image_task.progress, image_task.prefix, dir_name=image_task.prefix+'/color_'+image_task.raw_dir)

                            data['points'] = []
                            data['image_type'] = 'color'
                            data['laser_index'] = None
                            self.output_q.put(data)

                        if (image_task.task_type == "PROCESS_DEPTH_IMAGE"):
                            #self._logger.debug('Image Processing starts.')
                            try:
                                #TODO: Save image here for creating debug information.
                                if bool(self.config.file.keep_raw_images):
                                     self.image.save_image(image_task.image, image_task.raw_image_count, image_task.prefix ,
                                                           dir_name=image_task.prefix + '/raw_laser_' + image_task.raw_dir)

                                color_image = None
                                image_task.image = self.image_processor.rotate_image(image_task.image)
                                angle = float(image_task.progress * 360) / float(image_task.resolution)

                                if bool(self.settings.file.color):
                                    color_image = self.image.load_image(image_task.progress,
                                                                        image_task.prefix,
                                                                        dir_name=image_task.prefix+'/color_'+image_task.raw_dir)

                                point_cloud = self.image_processor.process_image(angle,
                                                                                 image_task.image,
                                                                                 color_image,
                                                                                 index=image_task.index)

                                data['point_cloud'] = point_cloud
                                data['image_type'] = 'depth'
                                data['laser_index'] = image_task.index

                                point_cloud = None
                                color_image = None

                            except Exception as e:
                                self._logger.exception(e)
                            self.output_q.put(data)

                    image_task = None
                except Empty:
                    time.sleep(0.1)
                    pass
            else:
                # thread idle
                time.sleep(0.1)

        self._logger.debug("Killed Worker Process with PID " + str(self.pid))