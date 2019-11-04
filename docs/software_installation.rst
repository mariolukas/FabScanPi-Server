.. _software_installation:

***********************
Installing the Software
***********************

There ist no need to flash the Arduino which is located on the FabScan PI HAT. It will be flashed automatically with the current firmware version after the server is started.

Using the Image (recommended)
-----------------------------

The fastest way to start working with FabScan PI is to use the FabScan PI Raspbian Image.

For the installation you will need the following things:

- A computer with integrated or connected card reader
- A Micro-SD card with at least capacity of 8 GB
- A software to format the SD card (e.g. [SD-Formatter](https://www.sdcard.org/downloads/formatter_4/))
- A software to install the image on the SD card (e.g. [Win32DiskImager](https://sourceforge.net/projects/win32diskimager/))
- The latest [FabScan PI Raspbian image](https://github.com/mariolukas/FabScanPi-Build-Raspbian/releases/latest)

Download the SD-Formatter an the Win32Disk image software and install them on your computer. Tip: During the installation takes place you can already download and unzip the latest FabScan PI image and save some time. In the end you should have a file with .img extension.

Now insert the Micro-SD card into the card reader which is connected with your computer.

.. image:: images/SD-Formatter_1.jpg
   :alt: SD Formater

Start the SD-Formatter software and select the correct device letter. Double-check that because otherwise there is a risk of formatting another drive.

.. note:: The displayed size of the selected card my vary from the physical size. This is because of an old image which is already installed on the card.

Click on the "Format" button to format the selected SD card.

.. image:: images/SD-Formatter_2.jpg
   :alt: SD Formater


When the formatting process is completed an information window will pop-up. Leave the card in the reader.

.. image:: images/SD-Formatter_3.jpg
   :alt: SD Formater

Exit the SD-Formatter and start the Win32DiskImager for transferring the image on the freshly formatted card.

.. image:: images/Win32DiskImager_1.jpg
   :alt: SD Formater

Select same device as before in the SD-Formatter software. Click on the folder icon and select the image file in your file system. Normally it should be in your browser's download folder. Make sure to unzip it first to get the image with .img extension.

.. image:: images/Win32DiskImager_2.jpg
   :alt: SD Formater

Click on the "Write" button and the installation process will begin to start. When it's finished you will be informed by a pop-up.  Click on the "exit" button to close Win32DiskImager.

.. image:: images/Win32DiskImager_3.jpg
   :alt: SD Formater


Now your SD-Card is ready to be put into the card slot of your FabScanPi.

After the image is flashed and the Raspberry Pi is up and running follow the instructions in the [Usage section](https://github.com/mariolukas/FabScanPi-Server/blob/master/README.md#useage)


Installing from deb packages
----------------------------

This description assumes that you have a SD card with a fresh Raspbian image on it.

First add the fabscan repository to your source list.

.. code:: bash

    echo "deb http://archive.fabscan.org/ jessie main" >> /etc/apt/sources.list


Then add the FabScan PI repository key to your key chain.

.. code:: bash

    wget http://archive.fabscan.org/fabscan.public.key -O - | sudo apt-key add -


Update the package list.

.. code:: bash

    apt-get update

Finish the installation with the needed packages.

.. code:: bash

    apt-get install fabscanpi-server python-opencv-tbb libtbb2  python-pil python-serial python-pykka python-picamera avrdude python-semver python-scipy


The FabScan PI server can be started with

.. code:: bash

    sudo /etc/init.d/fabscanpi-server start


Read [Usage](https://github.com/mariolukas/FabScanPi-Server/blob/master/README.md#useage) section for the next steps.



Building a custom image
-----------------------

The image can be build with the FabScanPi Image build script. You will find more

information [here](developing.md#Building FabScanPi Images)



Installing from Source
----------------------

Dependencies

FabScan PI software depends on some python libraries. You need to install pyserial, pykka, opencv with tbb support
and picamera. The easiest way to install all dependencies is to use debians package manager apt. Some of the packages,
like opencv with tbb support and libtbb are not provided by the official raspbian mirrors. You need to add the
fabscan repository to your apt source list.

Build Debian package
Install dependencies

.. code:: bash

    sudo apt-get install build-essential dpkg-dev debhelper devscripts fakeroot cdbs python-setuptools python-support


The package is build by calling

.. code:: bash

    make deb

Afterwards the package can be installed by

.. code:: bash

    dpkg -i fabscabpi-server<package-version>.deb





