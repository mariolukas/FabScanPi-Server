__author__ = "Mario Lukas"
__copyright__ = "Copyright 2015"
__license__ = "AGPL"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"


import abc
from fabscan.util.FSSingleton import SingletonMixin

class FSAbstractHadrwareController(SingletonMixin):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(FSAbstractHadrwareController, self).__init__()
        pass

    @abc.abstractmethod
    def settings_mode_on(self):
        pass

    @abc.abstractmethod
    def settings_mode_off(self):
        pass

    @abc.abstractmethod
    def get_picture(self):
        pass

    @abc.abstractmethod
    def camera_is_connected(self):
        pass