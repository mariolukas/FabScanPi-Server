import logging
class FSHardwareConnectorInterface:

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def move_turntable(self, steps, blocking):
        """
        Moves the turntable motor.
        Parameters
        ----------
        steps : int
            number of steps to move the turntable
        blocking : boolean
            defines if the motor moves are blocking or not
        """
        raise NotImplementedError("Can't use 'move turntable' on an this type of scanner")

    def laser_on(self, number):
        """
        Switches the laser on
        Parameters
        ----------
        number : int
            number of the laser
        """
        raise NotImplementedError("Can't use 'laser on' on an this type of scanner")

    def laser_off(self,  number):
        """
        Switches the laser off
        Parameters
        ----------
        number : int
            number of the laser
        """
        raise NotImplementedError("Can't use 'laser off' on an this type of scanner")

    def light_on(self, red, green, blue):
        """
        Switches the led on
        """
        raise NotImplementedError("Can't use 'light on' on an this type of scanner")

    def light_off(self):
        """
        Switches the led off
        """
        raise NotImplementedError("Can't use 'light off' on an this type of scanner")
