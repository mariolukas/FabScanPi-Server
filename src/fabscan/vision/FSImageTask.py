__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

class FSTaskType(object):
    PROCESS_COLOR_IMAGE = "PROCESS_COLOR_IMAGE"
    PROCESS_DEPTH_IMAGE = "PROCESS_DEPTH_IMAGE"
    PROCESS_PREVIEW_IMAGE = "PROCESS_PREVIEW_IMAGE"
    KILL = "KILL"

class ImageTask(object):

    color_image = None
    laser_image = None
    progress = 0
    raw_dir = "raw"
    resolution = 100
    state = None

    def __init__(self, image, prefix, prorgess, resolution=100, task_type="PROCESS_DEPTH_IMAGE", settings=None, raw_dir="raw", index=None):
            self.image = image
            self.progress = prorgess
            self.raw_dir = raw_dir
            self.resolution = resolution
            self.task_type = task_type
            self.prefix = prefix
            self.settings = settings
            self.index = index