.. FabScanPi - Open Source 3D Scanner documentation master file, created by
   sphinx-quickstart on Sat Aug 31 10:20:00 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#####################################
Welcome to FabScanPi's documentation!
#####################################


.. image:: images/logo.jpg
   :alt: FabScanPi Logo
   :align: right

About the Project
--------------------

FabScan is an open source 3D laser scanner. The `project <http://hci.rwth-aachen.de/fabscan>`_ started in 2010 at
`Germany's first FabLab in Aachen <http://hci.rwth-aachen.de/fablab>`_. The FabScan PI is the next generation of the FabScan 3D Laser Scanner
and since 2015 Mario Lukas took over as the lead developer of the project. The project is a community and spare time driven project.

Even if it looks like a team of many people is working in it, mostly only two or three people are working on the
current branch ( please thing about it while you are waiting for support ).

The core of the project is based on a Raspberry Pi and a Raspberry Pi camera module. With those components the scanner
can be driven standalone. It can be controlled over a web-enabled frontend.



Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   first_steps

.. toctree::
   :maxdepth: 2
   :caption: Hardware

   hardware_bom
   hardware_case
   hardware_electronics

.. toctree::
   :maxdepth: 2
   :caption: Software

   software_installation
   software_updates
   software_configuration
   software_usermanual
   software_troubleshoot

.. toctree::
   :maxdepth: 2
   :caption: Calibration

   scanner_calibration

.. toctree::
   :maxdepth: 2
   :caption: Development

   development_backend
   development_frontend
   development_firmware
   development_raspbian

.. toctree::
   :maxdepth: 2
   :caption: Contribution

   contribution.rst
   community.rst
