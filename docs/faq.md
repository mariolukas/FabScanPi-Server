**F.A.Q.**

**[Software](#software)**

**[Hardware](#hardware)**

**[Scanning Issues](#scanningIssues)**

**[Other](#other)**



------

#### Software<a name="software"></a>

- What username and password do I need for login the FabScanPi?

The username / password is the same as in the standard raspbian configuration: 

Username: **pi**
Password: **raspberry**




- What are the standard values in the config-file for the box dimensions?

The values may vary a bit, depending on your assembly. But for getting started these values can be used:


|                | x-value | y-value | z-value |
| -------------- | :-----: | :-----: | :-----: |
| Camera         |    0    |   6.6   |   24    |
| Laser          |   10    |   7.3   |   20    |
| Turntable      |    0    |    0    |   7.5   |
| Scanner origin |   n/a   |  0.69   |   n/a   |

|                 | Frame value |
| --------------- | :---------: |
| Frame dimension |     24      |

Note: Unit for all values is centimeters [cm].



------

#### Hardware<a name="hardware"></a>

- ##### What power source(s) do I need to get my FabScanPi working?

The FabScanPi will need 12V DC and 5V DC. There are different options to fulfil this requirement:



**Option A:** Connect 12V DC to the HAT (round connector) and install a 12V DC - to - 5V DC regulator on the designated space on the HAT. 

NOTE: For details and specifications please consult the hardware chapter.



**Option B:** Connect 12V DC to the HAT (round connector) and 5V DC to the raspberry (micro USB 								connector). 

NOTE: Make sure you switch on the both power sources at the same time to avoid software trouble.



**Option C:** Connect 12V DC to the HAT (round connector) and connect a 5V DC power source to the 5V pin regulator pin on the HAT. 

NOTE: For details and specifications please consult the hardware chapter.



- ##### What is the rotating direction of the scan table?

It should move clockwise – if not please consult the hardware chapter of our documentation and check the connection of your stepper.



- ##### What camera will work?

FabScan Pi can be built with both Raspberry Pi Camera Modules V 1.x or V 2.x.



- ##### Is the LED-Ring / PCB-board with LEDs mandatory?

No, you can start without the LEDs when you only need un-textured scans. To archive good quality texture scans we highly recommend the use of an LED light source.



- ##### Which LED-ring is compatible?

Any ring using WS2812B LEDs (or compatible) will do.



- ##### I have a Raspberry Cam Module with NoIR. Can I use it?

There’s no advantage in using the NoIR cam. The algorithms for the laser detection are made for 
the normal cam. Therefore we recommend to use the normal camera modules.



------

#### Scanning issues<a name="scanningIssues"></a>

- ##### The turntable is jerking during the scan process what can I do?

This behavior is quite normal because every time a new image has been shot the table just moves to the next position. If the table is turning smoothly (clockwise) during scan preview everything should be fine.



- ##### My scan is cut-off on top and / or bottom. What can I do?

Try to optimize your scan results by changing the “dimension” value.



- ##### The texture scan is mirror-inverted.

Check the rotating direction of your turntable (and the connection of the stepper motor). Check and adjust your config-settings for the “dimension”-value.



- ##### The laser cannot be detected.

Make sure your laser adjustment is correct. The laser must pass the scanning table right through the center. If no object is on the table the laser should be visible in the preview image (on the rear wall close to the left border of the image).



- ##### The scans don’t have the same shape as the original.

Check if your laser is aligned in vertical direction.



------

#### Other<a name="other"></a>

tbd.
