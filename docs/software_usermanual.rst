.. _software_usermanual:

******************
Using the Software
******************

**Getting Started**

- By default the FabScanPi server binds to all interfaces on port 8080. Pointing your browser to http://ip-of-your-raspberry-pi:8080 will open the user interface.

  If your FabScanPi has access to the internet an information window with the latest project news will pop-up. You can close it by left-clicking on the black x in the upper right corner of the grey info window. If there is a new software version available you will see a note in the upper left corner:

.. image:: images/Manual_UpdateAvailable_1.jpg


First start-up
--------------

Before you proceed with the calibration and your first scan please check a few things to ensure your FabScanPi is working properly:

- Click on the duck icon (New Scan) to enter the scan menu.
- Now the turntable should turn clockwise in a constant smooth manner.
- The laser must be on and needs to be adjusted vertically and to cross the center of the turntable. You will have to do the adjustment by hand because the servo / stepper support for the laser has not been implemented yet.
- Check if you can see a small video preview in the lower left corner of the scan menu. Maybe there is only a turning hour glass visible. That is a known problem of some browsers but will have not effect the scanner's function.
- Click on the X (Cancel) to get back to the main menu.


Scanner Calibration
-------------------

Before you can start with your first scans you must perform a calibration. That is necessary because every Scanner housing is a bit different.  By calibrating your scanner the software will get the exact parameters of your FabScanPi. You will have to do the calibration only once, the gathered data will be stored. But we recommend to do a calibration every time when the FabScanPi has been shipped, modified or when the scan results look distorted.

.. note:: Only after finishing the calibration successfully you will have good scan results .

The calibration will be done by scanning an calibration sheet with a specific pattern which must be placed on the turntable. The pattern must face the camera:


.. image:: images/calibration_start_position.jpg

Option 1: You can can build your own calibration tool from cardboard. Print the calibration sheet onto paper and glue it to cardboard. Build a stand of another piece of cardboard. Maybe you have to fix the calibration sheet on the turntable by using some adhesive tape.

Option 2: You have an 3D-printer available and can print out our calibration sheet holder. There's also a different calibration sheet for external holder use.


.. note:: To get a perfectly flat and stable surface glue the calibration sheet on a piece of thick pcb (printed circuit board).

 `Download calibration mount and sheet! <https://github.com/mariolukas/FabScan-Case/tree/master/calibratio>`_

Version V1 and V2 have the same size. Both will fit. But V2 is more printer friendly.


.. note:: Please check if your print of the calibration sheet has the correct scale. Each black square should have the same side length as stated on the calibration sheet (e.g.11 mm (1,1 cm). If the size is not correct please correct the parameter "pattern square size" in the configuration file.

You can find all details in the chapter :ref:`How to Edit the Config File` .

Place the calibration sheet on the turntable facing the camera. See `here <configuration.html#how-to-edit-the-config-file>`_


.. image:: images/calibration_start_position.jpg



Please close the box to avoid external light sources to impact the calibration process. Start  your browser and call http://ip-of-your-raspberry-pi:8080 which will open the user interface.



When you start your FabScanPi for the first time you will see an information in the upper left corner that you have to perform a calibration.

.. image:: images/Manual_NoCalibration_1.jpg



Start the calibration procedure by clicking on the gun sight icon in the very upper left corner.

.. image:: images/Manual_1.jpg



An information "Calibration started" will be displayed in the upper left corner.

.. image:: images/Manual_2a.jpg



The calibration may need several minutes. During the calibration an information about the remaining time is displayed.

.. image:: images/Manual_2b.jpg



When the calibration was finished successfully another notification will appear for a short time in the upper left corner.

.. image:: images/Manual_2c.jpg

Now you can remove the calibration pattern sheet from the turntable and start your first scan.

.. note:: If your scan results look not like they should, probably distorted or skewed please check the calibration data in the configuration file. You can find details about the different relevant parameters in the [Config File Values](#config-file-values) section of this documentation.

Settings
--------

.. note:: The current settings are only persistent as long as the pi is up and running. The settings are saved with the scan data after a successful scan. They can be loaded to scan another object with the same settings. E.g. an object what consists of the same material, color etc.

- Click on the duckling-symbol to open the scan menu.

.. image:: images/Manual_4.jpg



- The threshold-slider (6) can be used to adjust the sensitivity of the captured data. Select the scan quality by using the other slider (7).

.. note:: The better the scan the longer is the required capture time. Sometimes it is better to start with a low resolution to control the selected settings result. If the result is nice you can perform a higher resolution scan with the same settings.

.. image:: images/Manual_5a.jpg


By clicking on the contrast-icon (3) you will get access to the camera settings menu. For adjusting the camera presets three sliders for saturation, brightness and contrast are available.


.. image:: images/Manual_6.jpg


Click on the light-symbol (4) to get access to the lighting menu.

.. image:: images/Manual_5a.jpg



Here you can use the sliders to change the brightness and color of the (optional) light source. When all three sliders are at the very left end the light is off. Watch the preview in the lower left corner of the menu.

.. image:: images/Manual_7.jpg

.. note:: The setting in the lighting menu will only cause an effect if an optional WS2812-compatible light source (e.g. Adafruit NeoPixel LED-Ring or FabScanPi-Camera-Holder) is installed. Click on the  arrows-and-circle symbol (5) to get access to the alignment menu.

.. image:: images/Manual_5a.jpg

Perform a San
-------------


Scan with Color (slower)
~~~~~~~~~~~~~~~~~~~~~~~~

- Make sure your FabScanPi is switched on, an object is placed on the turntable and the lid / the optional laser safety switch is closed.
- Open the web-interface as described in chapter
  [Getting Started](#gettingStarted).
- Click on the duckling-symbol to open the scan menu.

.. image:: images/Manual_4.jpg



.. note:: If you do not have installed a light source you should perform a [monochrome scan](#monochromeScan).

- Adjust the scan preset values to your needs as described in chapter [Presets](#presets).

.. image:: images/Manual_TextureScan_1.jpg



- Click on .Start Scan. to initiate the process
  A starting message will be displayed. Now the texture will be processed.


.. image:: images/Manual_TextureScan_2.jpg


The latest photo will be displayed during the capturing process.

.. image:: images/Manual_TextureScan_3.jpg



When the texture has been captured (progress bar at 50 percent) the actual scan is initiated. A notification is displayed.

.. image:: images/Manual_TextureScan_4.jpg


A notification will be displayed when the scan is completed / file is saved.

.. image:: images/Manual_TextureScan_5.jpg


- You can now check, download or delete the scan-data.


Scan without Color (faster)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Make sure your FabScanPi is switched on, an object is placed on the turntable and the lid / the optional laser safety switch is closed.
- Open the web-interface as described in chapter
  [Getting Started](#gettingStarted).
- Click on the duckling-symbol to open the scan menu.

.. image:: images/Manual_4.jpg


- Adjust the scan preset values to your needs as described in chapter [Presets](#presets).
- Uncheck the color-scan option (8)

.. image:: images/Manual_5a.jpg


- Click on .Start Scan. to initiate the process
  A starting message will be displayed and the scan process is started.

.. image:: images/Manual_Scan_2.jpg



When the scan is completed / file is saved a notification will be displayed.

.. image:: images/Manual_Scan_3.jpg


- You can now check, download or delete the scan-data.

Generate Mesh
-------------

The FabScanPi software includes a feature to convert a scan into a mesh-file. This mesh-file can be used for 3D-printing.

.. note:: To generate a mesh-file a scan must have been performed. It is also possible to load a scan-file which has been saved previously.

- Click on the options icon to open the options menu.

.. image:: images/Manual_CreateMash_1.jpg



- The options menu will open and you can see the index card of the loaded file.

.. image:: images/Manual_CreateMash_1.jpg



- Click on the magic wand icon to open the menu for the MeshLab filter.

.. image:: images/Manual_CreateMash_3.jpg



- Now select one of the Meshlab filters and the file format for the future mesh file.

- Click on "Start Meshing" to activate the conversion process.

.. image:: images/Manual_CreateMash_4.jpg



The conversion starts and the main menu appears. A notification is displayed as well.

.. note:: Depending on the size and complexity of the scan file as well as the type of selected filter the conversion process may take some time.

.. image:: images/Manual_CreateMash_5.jpg



When the mesh-file is available a notification is displayed.

.. image:: images/Manual_CreateMash_6.jpg



- Again open the options menu. Another index card for the mesh-file has been added.

- Click on the mesh-file index card.

- You can now click on the download-icon to download the mesh-file to your computer or click on the trashbasket icon to delete the mesh-file.

.. image:: images/Manual_CreateMash_8.jpg


File Operations
---------------

- Load files

A scan result which has been saved to the FabScanPi memory previously can be reloaded. Go to the main menu and click on the folder-icon at the left side of the menu bar.

.. image:: images/Manual_LoadScan_1.jpg

- Scroll through the displayed file inventory and click on the icon of the wanted file.

.. image:: images/Manual_LoadScan_2.jpg



Now the selected file will be loaded which may need some time. After the loading process is finished a notification will be displayed.

.. image:: images/Manual_LoadScan_3.jpg


Delete a Scan
-------------

- Delete files

**Delete a scan-file**

A scan result which has been saved to the FabScanPi memory previously can be deleted. To do that it must be loaded and displayed on the virtual turntable in the main menu.
-Click on the options-icon on the right side of the menu bar.

.. image:: images/Manual_CreateMash_1.jpg

Click on the wastebasket-icon to delete the scan-file.

.. note:: By deleting a scan file the corresponding mesh file (if available) will be deleted instantly.


**Delete a mesh-file**

Note: If a mesh file is available a second slide for the mesh file will be displayed.

.. image:: images/Manual_CreateMash_1.jpg


By selecting the mesh slide and clicking on the wastebasket-icon the mesh-file can be deleted separately.

.. image:: images/Manual_DeleteScan_1.jpg

- Download Files
  It is possible to download generated files (either scan- or mesh-files) from the FabScanPi via the web-based user interface.

Download Results
----------------

**Download a scan-file**

Note: Before you can download a file it must be [loaded](#loadFiles) and displayed on the virtual turntable in the main menu.

- Go to the main menu.

- Click on the options-icon on the right side of the menu bar.


.. image:: images/Manual_CreateMash_1.jpg

- Click on the download-icon to download the mesh-file

- A download message (depending on the used web-browser) will be displayed

**Download a mesh-file**

Note: If a mesh file is available a second slide for the mesh file will be displayed.

.. image:: images/Manual_CreateMash_1.jpg

- Select the mesh slide
- Click on the download-icon to download the mesh-file
- A download message (depending on the used web-browser) will be displayed

