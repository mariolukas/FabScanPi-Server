.. _first_steps:

***************
First Steps
***************

.. image:: images/FabScanPI_closed.jpg
   :alt: FabScan case closed
   :width: 220

.. image:: images/FabScanPi_opened.jpg
   :alt: FabScan case opened
   :width: 300


Build your FabScan
------------------

You can purchase the FabScanPi as a kit or in parts at `Watterott Electronics <http://www.watterott.com>`_

* `FabScanPi Kit <https://shop.watterott.com/FabScan-Pi-Kit-with-Raspberry-Pi-3>`_ ( contains all needed parts )
* `FabScanPi HAT <https://shop.watterott.com/RPi-FabScan-HAT-for-FabScan-Pi-3D-Scanner-Project>`_ ( a Raspberry Pi HAT for FabScan )
* `FabScanPi Camera Mount <https://shop.watterott.com/Raspberry-Pi-Camera-Ring-Light-JST>`_ ( Raspberr`y Pi cam mount with LED's)
* `FaBScanPi Case <https://shop.watterott.com/FabScan-Pi-Housing-Parts-V2>`_ ( laser cut wooden case parts )

But you can also build one by yourself. All needed files are located at `GitHub <https://github.com/mariolukas/FabScan-Case>`_.

Get the latest Software
-----------------------

The fastest way to use the FabScanPi is to use the FabScanPi Raspbian ISO image.
Connect all needed hardware parts, download and flash the latest ISO image:

.. raw:: html

    <iframe src="_static/releases.html" marginwidth="0" marginheight="0" scrolling="no" style="width:100%; height:100%; border:0; overflow:hidden;">
    </iframe>


Open the User Interface
-----------------------

You have to unzip the file to get the .img file. After flashing the image to an SD card point your browser to

    http://[ ip-address-of-your-raspberry-pi ]

It is also possible to join the web-enabled FabScanPi user interface by pointing your browser to

    http://fabscanpi.local

.. note:: Calling fabscanpi.local requires zeroconf. This is povided by default on Apple devices. For Windows you will needto install the `Bonjour printer driver <https://support.apple.com/kb/DL999>`_ to access your FabScanPi over thelocal address.

