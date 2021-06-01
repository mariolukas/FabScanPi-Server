from os import path
import subprocess
import time
import logging

class ThrottledState:
    UNDER_VOLTAGE_ACTIVE = 1 << 0
    ARM_FREQUENCY_CAPPING_ACTIVE = 1 << 1
    THROTTLING_ACTIVE = 1 << 2
    SOFT_TEMPERATURE_LIMIT_ACTIVE = 1 << 3

    UNDER_VOLTAGE_HAS_OCCURRED = 1 << 16
    ARM_FREQUENCY_CAPPING_HAS_OCCURRED = 1 << 17
    THROTTLING_HAS_OCCURRED = 1 << 18
    SOFT_TEMPERATURE_LIMIT_HAS_OCCURRED = 1 << 19

_logger = logging.getLogger(__name__)

def get_cpu_temperature():

    temp_check_path = "/sys/class/thermal/thermal_zone0/temp"

    if path.exists(temp_check_path):

        with open("/sys/class/thermal/thermal_zone0/temp") as tmpFile:
            cpu_temp = tmpFile.read()
            cpu_temp = float(cpu_temp) / 1000
            cpu_temp = float("{0:.2f}".format(cpu_temp))
    else:
        _logger.warning("Not able to estimate system temperature.")
        cpu_temp = 0.0

    return cpu_temp


def _vcgencmd_get_throttled():
    try:
        output = subprocess.check_output(["vcgencmd", "get_throttled"]).decode()
        output = int(output.strip().split("=")[1], 16)
    except Exception as e:
        output = 0
    return output


def get_throttle_state():
    throttled_state = _vcgencmd_get_throttled()
    if throttled_state & ThrottledState.UNDER_VOLTAGE_ACTIVE:
        _logger.warning("Under-voltage detected")
    if throttled_state & ThrottledState.ARM_FREQUENCY_CAPPING_ACTIVE:
        _logger.warning("Arm frequency capped")
    if throttled_state & ThrottledState.THROTTLING_ACTIVE:
        _logger.warning("Currently throttled")
    if throttled_state & ThrottledState.SOFT_TEMPERATURE_LIMIT_ACTIVE:
        _logger.warning("Soft temperature limit active")
    if throttled_state & ThrottledState.UNDER_VOLTAGE_HAS_OCCURRED:
        _logger.warning("Under-voltage has occurred")
    if throttled_state & ThrottledState.ARM_FREQUENCY_CAPPING_HAS_OCCURRED:
        _logger.warning("Arm frequency capping has occurred")
    if throttled_state & ThrottledState.THROTTLING_HAS_OCCURRED:
        _logger.warning("Throttling has occurred")
    if throttled_state & ThrottledState.SOFT_TEMPERATURE_LIMIT_HAS_OCCURRED:
        _logger.warning("Soft temperature limit has occurred")
