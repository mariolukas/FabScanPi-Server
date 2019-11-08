.. _hardware_electronics:

***************
The Electronics
***************


About the FabScanPi HAT
=======================


The FabScan HAT is basically a combination of an [Arduino](https://www.arduino.cc/) and the old
[FabScan Shield](https://github.com/watterott/FabScan-Shield) for [Arduino](https://www.arduino.cc/). It provides all connectors for the hardware
parts (like motors, servos, lasers, LED's etc.) Instead of an USB
connection to the Raspberry Pi, the HAT is attached on the Pi's pinheaders.
The HAT communicates over a serial connection with the Rasperry Pi.
(GPIO14 and GPIO15 of the Raspberry Pi). The firmware and also updates are
flashed automatically by the FabscanPi-Server application.

.. image:: images/fabscanpihat.png


Assemble the FabScanPi HAT
==========================


.. note:: About soldering: If you are soldering for the very fist time, we suggest to read the comic ["Soldering is Easy"](https://mightyohm.com/files/soldercomic/FullSolderComic_EN.pdf) by Mitch Altman (soldering wisdom), Andie Nordgren (comic adaption) and Jeff Keyzer (layout and editing)._


.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/DogfNxk277Y" frameborder="0" allowfullscreen></iframe>


The FabScanPi HAT will be delivered with the main components already assembled. You only need to install the headers and connectors which fit your demand.

.. image:: images/hat_assembly_1.jpg
   :width: 400


Let's start with the female 8-pin headers for the stepper motor controllers. First the two headers which are designated with "Stepper Turn Table". Put one in and flip the pcb to solder the pins on the rear side. Solder one pin first and make sure the header is still in the correct position. A "third hand" tool or a pcb-holder are very helpful for this job.



Now you can select between three options

- **Option A:** Two stepper motor ports for the laser adjustment or

- **Option B:** Two servo connector ports for the laser adjustment or

- **Option C:** Two stepper and two servo connector ports for the lasers (additional headers required)

  ​

**Option A:**

Use the remaining four 8-pin femal pin headers and install them on the pcb. You can now use the HAT with three stepper motors (1x turn table, 2x laser control)

.. image:: images/hat_assembly_2a.jpg
   :width: 400


**Option B:**

Use an electronics wire cutter to cut off two 3-pin male headers from the long male-header. Put them into the pinholes labeled "Servo opt." You can now use the HAT with one stepper motors (1x turn table) and two servos (2x servo opt.).

.. image:: images/hat_assembly_2.jpg
   :width: 400


**Option C:**

If you are unsure about using servos or stepper motors you can install both. Therefore you'll need to buy four 8-pin female headers which are at least 8 mm of height. Install them at the pinholes for the "Stepper Laser 1 and 2". Also cut off two 3-pin male headers from the long male-header. Put them into the pinholes labeled "Servo opt." Now you can use either servo controllers nor the connectors for the servos.

.. image:: images/hat_assembly_2b.jpg
   :width: 400

**Connector for the LED-Ring**

The next connector is the JST connector for the RPi-RingLight. Make sure the direction is correct. Fix it and solder the three pins on the rear side of the PCB.

.. image:: images/hat_assembly_3.jpg
   :width: 400


The pins of the JST connector on the HAT have the following configuration:

.. image:: images/JST-HAT-Configuration.jpg
   :width: 400


**Connectors for the stepper motors**

Here you can use the three 4-port screw terminals if your stepper cables have no connector plug.

.. image:: images/hat_assembly_4.jpg
   :width: 400

If the stepper motor cables have an 4-pin female connector you can use three 4-pin male headers (to be cutted off from the long header).

.. image:: images/hat_assembly_4a.jpg
   :width: 400


**Connector for Laser(s) and Laser safety switch**

The next connector to be installed is the 6-port screw terminal. It must be soldered into the corresponding pin holes between the JST connector and the 8-pin female header for the table stepper. Later this 6-port terminal will be used to connect the Laser(s) and the Laser safety switch.

.. image:: images/hat_assembly_5.jpg
   :width: 400


**Power Connector** (DC- jack)

Now the DC-jack power connector will be installed into three oval pin holes across from the 2x20-pin socket header. Soldering is done from the top side of the PCB.

.. image:: images/RPi-FabScan-HAT13.jpg
   :width: 400


**Assembling the Raspberry-Pi Connector**

Now the 2x20-pin socket connector must be installed from the rear side of the PCB (where we only did soldering till now). Soldering of the 2x20-pin connector is done on the front side (where all our parts are placed). This connector is used as interface for the Raspberry-Pi.

.. image:: images/hat_assembly_7.jpg
   :width: 400

.. attention:: The power connector in the image above image is soldered in an alternative way. The recommended way is shown in the second last image.



The center pin is for +12V DC, the outer connector tongue is for GND.

.. image:: images/Power_Connector_HAT.jpg
   :width: 400


**Mount the 5V DC/DC converter or 5V external Power Source**

Additionally to the 12V DC coming from the power supply the FabScanPi needs 5V DC. Now you have to decide if you want to use a DC/DC converter IC which generates the 5V out of the 12V from the external 12 power supply (common solution).

For the DC/DC converter option you can find further instructions and pictures on the [Watterott electronic website](https://github.com/watterott/RPi-FabScan-HAT/blob/master/hardware/RPi-FabScan-HAT_Assembly.pdf).



If you are using another power supply which is capable of delivering 12V and 5V DC you can connect it as well. Details can be found [here](#5V-EXT).



#Connecting the Stepper Motor(s)


There are different kinds of stepper motos. Mostly with 4 or 6 leads. For
connecting the stepper motor to the FabScanPi HAT you need to know the
corresponding lead pairs of the motor coils. The best way to find out something
about the motor is to have a look at the datasheet of the motor manufacturer.
In the following desciptions the pairs are called (2B, 1B) and (1A, 2A).

.. image:: images/4wires.jpg
   :width: 400
.. image:: images/6wires.jpg
   :width: 400

There are several ways to find the pair wires without a datasheet. Some of them
are described here:

**Method with an ohm-meter**

Simply measure pairs of wires for their resistance. If the resistance is a few ohms
( < 100 Ω) only, you've found a pair. The other two wires should make up the other pair.

**Methods without an ohm-meter**

First, try turning the motor with your fingers, and notice how hard it is. Then,
stick wires together in pairs. If the motor turns noticeable harder, you've found a pair.
Another method is to use an LED, hold any two wires to the ends of a LED and turn the
motor (twiddle in both directions), the LED will light if the wires are a pair,
swap wires until you light the LED.


.. image:: images/hat_wires.jpg
   :width: 400


#Connecting the Lasers

The FabScanPi HAT provides connectors for two lasers. But only one laser
is supported until now. Connect your laser to the connectors labeled
with ...

.. image:: images/laser_connection.jpg
   :width: 400

**Safety switch**

There is the possibility to add a laser safety switch which disables the laser
when the lid is opened. The FabScanPi HAT provides a connector for such a switch.
If you don't need a switch you still have to bridge this connector with
a cable to get the lasers work. (left image: with bridged connector,
right image: connecting a switch)

.. image:: images/laser_safety.jpg
   :width: 400
.. image:: images/laser_safety_switch.jpg
   :width: 400



#Connecting the Motor drivers

TODO



#Connecting the Power Supply
The FabScanPi will need 12V DC and 5V DC. There are different options to fulfil this requirement:

**Option A:** (recommended)
Connect 12V DC to the HAT (round connector) and install a 12V DC - to - 5V DC regulator on the designated space on the HAT. Make sure the 5V power regulator can provide a current of min. 2.0A

for 1 turntable stepper motor, 1 PiCam and 1 laser.

.. image:: images/fabscanpihat_12to5.png
   :width: 400


+----------------+-------------------------------------------+
| Silk Label     | Description                               |
+================+===========================================+
| Inp.           | 12V from HAT as input for regulator       |
+----------------+-------------------------------------------+
| (white square) | Ground (GND)                              |
| 5V             | 5V output from regulator to FabScanPi HAT |
+----------------+-------------------------------------------+

For the DC/DC converter option you can find further instructions and pictures on the [Watterott electronic website](https://learn.watterott.com/fabscan/hat_assembly.pdf).


NOTE: For the final stage of constuction a more powerful power supply is needed. At the moment there are no technical specifications available.



**Option B:**

Connect 12V DC to the HAT (round connector) and 5V DC to the raspberry (micro USB connector).

NOTE: Make sure you switch on the both power sources at the same time to avoid software trouble.



**Option C:**

Connect 12V DC to the HAT (round connector) and connect a 5V DC power source to the 5V pin regulator pin on the HAT. Make sure the 5V power source can provide a current of min. 2.0A for

1 turntable stepper motor, 1 PiCam and 1 laser.



.. image:: images/fabscanpihat_5V.png
   :width: 400

+----------------+--------------------------------------+
| Pin label      | Description                          |
+================+======================================+
| (white square) | Ground (GND)                         |
+----------------+--------------------------------------+
| 5V             | Output from external 5V power source |
+----------------+--------------------------------------+

NOTE: For the final stage of constuction a more powerful power supply is needed. At the moment there are no technical specifications available. Make sure you switch on the both power sources at the same time to avoid software trouble.




#Connecting the LED Ring
This small manual will help you to assemble the Camera and LED ring combination. You will need a light if you want to perform texture scans (Check mark is set for Color Scan).

.. image:: images/RingLicht_1.jpg
   :width: 400

This is how it should look like if you finished the assembly.



The Ring-Light will include the  parts you can see in the next picture below (the camera modul is sold separately):

.. image:: images/RingLicht_1b.jpg
   :width: 400

IMPORTANT: You will need the standard camera modul (which has a green pcb). The module used in the pictures is the IR version which has the same dimensions but different optical specifications.



Step 1: Slide one end of the flat ribbon cable into the connector of the camera module (1). Make sure the blue plastic is on the side facing away from the camera. Push the lock bar of the connector gently into the lock position (2).

.. image:: images/RingLicht_2.jpg
   :width: 400



Step 2: Merge the flat ribbon cable through the elongated hole in the LED board.

.. image:: images/RingLicht_3.jpg
   :width: 400



Step 3: Put the four Screws through the holes in the camera board. The heads must be on the side where the lens is situated. Then put a spacer on every screw (as shown in the next picture).

.. image:: images/RingLicht_4.jpg
   :width: 400



Step 4: Put the Camera modul on the LED board. All four screws must fit the appropriate hole. This can be a bit tricky but it is doable.

.. image:: images/RingLicht_5.jpg
   :width: 400



Step 5: Put a nut on each screw an pull them hand-tight.

.. image:: images/RingLicht_6.jpg
   :width: 400

Now the Camera-LED assembly is ready for installation.



The pins of the JST connector on the LED board have the following configuration:

.. image:: images/JST-LEDboard-Configuration.jpg
   :width: 400



#Additional Motors for the Lasers

TODO

