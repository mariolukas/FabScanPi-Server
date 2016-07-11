__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

import abc

class FSAbstractImageProcessor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(FSAbstractImageProcessor, self).__init__()
        pass

    @abc.abstractmethod
    def process_image(self, angle, laser_image, color_image=None):
        pass