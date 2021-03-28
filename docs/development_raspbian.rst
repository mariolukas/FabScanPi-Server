.. _development_raspbian:

*************************
FabScanPi OS Image (Bash)
*************************

The FabScanPi OS image contains the FabScanPi OS. FabSanPi OS is a customized minimal Raspberry Pi OS which is
based on Debian ( formerly called Raspbian ).

This image can be built by using a docker container.

Obtaining the code
------------------

Checkout the FabScanPi OS image build script sources from Git. The default branch is the master branch.

.. code-block:: bash

    git clone https://github.com/mariolukas/FabScanPi-Build-Raspbian.git

Install Docker
--------------

You will need to install and run docker on your development machine. Just download and
install it from https://docs.docker.com/get-docker/

Then you need to install docker-compose. https://docs.docker.com/compose/install/

Build the Image
---------------

You can build the image on a Linux System by calling


.. code-block:: bash

    ./build-fabscan.sh

You can build the image on a OSX System by calling

.. code-block:: bash

    ./build-osx.sh

The finished build `image_<date>-FabScanPi-lite.zip` will be placed in the folder

.. code-block:: bash

    /FabScanPi-Build-Raspbian/pi-gen/deploy


