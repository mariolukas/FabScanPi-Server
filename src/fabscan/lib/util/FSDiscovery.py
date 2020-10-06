import json
import urllib.request, urllib.error, urllib.parse
import requests
import socket
import logging

try:
    import ssl
except ImportError:
    print("error: no ssl support")

_logger = logging.getLogger(__name__)

DISCOVERY_URL = "https://find.fabscan.org/register.php"

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def register_to_discovery(server_version, firmware_version):
    _logger.info("Trying to register ip "+get_ip()+" to discovery service.")

    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        'ip': str(get_ip()),
        'server_version': str(server_version),
        'firmware_version': str(firmware_version)
    }
    try:
        response = requests.post(DISCOVERY_URL, headers=headers, data=json.dumps(payload))

        response.raise_for_status()
        if response.status_code == 200:
            _logger.info('Successfully registered to find.fabscan.org')
        else:
            _logger.warn('Not able to register to find.fabscan.org')

    except requests.ConnectionError:
        _logger.warn('Can not register to FabScan Discovery Service, Device seems to be offline.')
