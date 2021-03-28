.. _development_firmware:

**************
Firmware (C++)
**************

The FabScanPi Firmware is the software which is running on the FabScanPi HAT (or Arduino used by other setups).

Obtaining the code
------------------

Checkout the FabScanPi OS image build script sources from Git. The default branch is the master branch.

.. code-block:: bash

    git clone https://github.com/mariolukas/FabScanPi-Firmware

Build with Arduino IDE
----------------------
TODO.

Build with Arduino CLI
----------------------

Install Docker
~~~~~~~~~~~~~~

You will need to install and run docker on your development machine. Just download and
install it from https://docs.docker.com/get-docker/

Then you need to install docker-compose. https://docs.docker.com/compose/install/

Run Build Process
~~~~~~~~~~~~~~~~~

Afterwards you can run the build process within a docker container, the docker container
includes all the tools needed for building the firmware, even all needed Arduino libraries
are pre-installed.

.. code-block:: bash

    ./build.sh

The script builds firmware (hex) files for all supported platforms (FabScanPi-HAT, Ciclop ZUM, Sanguinololu etc.).
Those hex files are named by the platform and build date.

`<platformname>_v.<yyyymmdd>.hex`

The files are located in the folder `build`.


Supported G-Codes
-----------------

*G01 [T(steps)]* - Move the Turntable for number of steps

*M4 [R(value) G(value) B(value)]* - Turn on LED Ring for given RGB-Vlaues

*M17* - Enable Motors

*M18* - Disable Motors

*M19* - Turn On Laser 0

*M20* - Turn Off Laser 0

*M21* - Turn On Laser 1

*M22* - Turn Off Laser 1

*M100* - Show Help Message