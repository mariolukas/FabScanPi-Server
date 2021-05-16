__author__ = "Mario Lukas"
__copyright__ = "Copyright 2017"
__license__ = "GPL v2"
__maintainer__ = "Mario Lukas"
__email__ = "info@mariolukas.de"

class Led:
    def __init__(self, hardware_connector):
        self.hardware_connector = hardware_connector
        self.is_on = False

    def on(self, red, green, blue):
        self.hardware_connector.light_on(red, green, blue)
        self.is_on = True

    def off(self):
        self.hardware_connector.light_off()
        self.is_on = False

