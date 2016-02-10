# Software 

### Installation

## Notice!
There ist no need to flash the Arduino firmware. It will be flashed automatically with the current
firmware version after the server is started.

#### Installation ISO Image (recommended)

The fastest way to start working with FabScan PI is to use the FabScan PI Raspbian Image. 
Dowload the image and install it to a SD-Card. After the image is flashed and the Raspberry
Pi is up and runnig follow the instructions in the [Usage Section](Readme.md#usage)

Latest image release: [https://github.com/mariolukas/FabScanPi-Build-Raspbian/releases/latest](https://github.com/mariolukas/FabScanPi-Build-Raspbian/releases/latest)

Ready to use images can be downloaded here or build by using the FabScanPi rasbian build
scipt (Debian/Ubuntu Linux only).

#### Installation clean Raspbian with FabScan PI repository

This description assumes that you have a SD card with a fresh Raspbian image on it. 

First add the fabscan repository to your source list. 

```
echo "deb http://archive.fabscan.org/ jessie main" >> /etc/apt/source.list
```

Then add the FabScan PI repository key to your key chain.

```
wget http://archive.fabscan.org/fabscan.public.key -O - | sudo apt-key add -
```

Finish the installation with the needed packages.

```
apt-get install fabscanpi-server python-opencv-tbb libtbb2  python-pil python-serial python-pykka python-picamera avrdude
```

The FabScan PI server can be started with 

```
sudo /etc/init.d/fabscanpi-server start
```

Read [Usage](Readme.md#usage) section for the next steps.

#### Installation form source

##### Dependencies

FabScan PI software depends on some python libraries. You need to install pyserial, pykka, opencv with tbb support 
and picamera. The easiest way to install all dependencies is to use debians package manager apt. Some of the packages, 
like opencv with tbb support and libtbb are not provided by the official raspbian mirrors. You need to add the
fabscan repository to your apt source list. 

### Build Debian package
Install dependencies
sudo apt-get install build-essential dpkg-dev debhelper devscripts fakeroot cdbs python-setuptools python-support

The package is build by calling

```
make builddeb
```

Afterwards the package can be installed by 

```
dpkg -i fabscabpi-server<package-version>.deb
```

### Setting up a WIFI connection

This description explains howto setup a wifi stick for raspbian. I prefer to use an EDIMAX dongle, it worked best for me. 
First plug in your wifi dongle and log in via ssh with password "raspberry" (without quotes):

```
ssh pi@<your-fabscanpi-ip>
```

Your fasbcanpi image is ready to go. The only thing you have to do is open wpa_supplicant.conf and 
insert your wifi ssid and your wifi secret.

```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Save the file and try to connect to your wifi by typing the following command.
```
sudo ifup wlan0
```

In some cases you have to reboot the Raspberry Pi. Check if the wifi dongle's led is bliking.
If you want to change your Raspberry Pi to a fix wifi IP address you have to change the interfaces file
to get a static wifi connection.

```
sudo nano /etc/network/interfaces
```

Change the files content from 

```
auto lo
iface lo inet loopback

allow-hotplug eth0
iface eth0 inet dhcp

auto wlan0
allow-hotplug wlan0
iface wlan0 inet dhcp
wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet dhcp
```

to 

```
auto lo
iface lo inet loopback

allow-hotplug eth0
iface eth0 inet dhcp

auto wlan0
allow-hotplug wlan0
iface wlan0 inet static
address <ip in your network>
netmask <your netmask>
gateway <your gateway>
wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet dhcp
```

After you changed the file you can restart your network daemon.

```
sudo /etc/init.d/networking restart
```

#### Configuration File

A configuration file can be found in /etc/fabscanpi/default.config.json. The content of this file 
is in JSON format and can be edited with an editor of your choice (e.g. nano). Be careful and don't
miss brackets. JSON is really sensitive in it's format.

##### Folders
In this section you can change the scan output folder and the folder where the ui is located. If 
you don't know what you are doing, it is a good decision to keep this section untouched.

```
   "folders" : {
    "www": "/home/pi/fabscan/src/www/",
    "scans": "/usr/local/fabscanpi/scans/"
   }
```

##### Serial 
In this section you can set your port. Some Arduino and compatible boards differ in the port name.
Due the FabScanPi is made to use the FabScanPi HAT the default value is /dev/ttyACM0. In most cases
this also works with an Arduino or compatible. 

The autoflash option is True by default, that means that the firmware is flashed automatically to 
the Arduino or FabScanPi HAT. If you want to use a custom board e.g. sanguinololu, you can set this
to False and flash the Firmware manually to your board. 
   
```
   "serial" : {
     "baudrate" : 115200,
     "port": "/dev/ttyACM0",
     "autoflash": "True"
   }
``` 

##### Camera 

In this section some camera values are set. The type can be set to PICAM which is default value. There is 
also an experimental mode for a C270 webcam. But this mode is not further developed. I used it in early 
versions of fabscanpi. 

The device is not used for the PICAM. Only if a webcam is used, you have to set the device to the count number
of your webcam if you have one or more cameras connected to your pi.

Preview Resolution is the resolution value for the settings window. 
Resolution is the resolution for the picamera python module. You can have a look to the documentation of 
picamera. If you set this to other values please be sure what you are doing, not all resolutions are supported
by the picam. Some might lead to slower image capturing. 

The position values are used to define where the camera is located in the case. All values are in cm. 
Thre is an image later in this documentation which explains all the dimension related meassures. 

Frame dimension is what your camera sees in the case. An easy way to validate this value is to put a 
ruler to the backwall of the fabscan ( i used a paper one from IKEA ). Then activate the settings mode
and read the last value you can read in the image. The default is 23.5 cm. The default value fits most
of the FabScan setups. This value is used for tansforming image coordinates to world coordinates. 

```
   "camera" : {
     "type" : "PICAM",
     "device" : 1,
     "preview_resolution":{
        "width": 320,
        "height": 240
     },
     "resolution":{
          "width": 1296,
          "height":972
      },
      "position":{
          "x": 0.0,
          "y": 5.5,
          "z": 27.6
      },
      "frame":{
          "dimension": 23.5
      }
   }
``   

##### Laser 
This section describes the laser position and laser stepper motor values. I mentioned position values in the section 
before (Camera), have a look at the image. 

The angle is set to the angle which was used in the last scan. The rotation_steps value should be used for a laser 
angle change (not implemented yet).Steps defines how many steps the motor can do. In the default case the motor is 
set to 1/16 step mode. A motor with 200 steps per turn can then perform 3200 steps. 

``` 
   "laser": {
      "position":{
        "x": 10.0,
        "y": 7.3,
        "z": 24.5
      },
      "angle": 33.0,
      "rotation_steps": 5,
      "steps": 3200
   }
```
   
   
##### Turntable
In this section some turntable related values are set. For positioning have a look to the image. 
Steps defines how many steps can be perfomed for a full rotation. This value depends on your motor and driver.
In the default case the motor is set to 1/16 step mode. A motor with 200 steps per turn can then perform 3200 steps.

```
   "turntable":{
     "position": {
       "x": 0.0,
       "y": 0.0,
       "z": 7.5
     },
     "steps":3200
   },
```
   
##### Scanner 
This section defines global scanner related values. Origin is defined as the green horizontal line in the settings
preview window. It is a also here a good idea to keep that value untouched. Process number defines how many processes
should be used for calculating the scan data. Due the Raspberry Pi2 serves 4 cores it is a good idea to keep this
value. Increasing the proccess number does not mean inrceasing speed in all cases. 
Meshlab is not supported in the curren verision of fabscan pi. So you can leave this value. 

```
   "scanner": {
      "origin":{
        "y" : 0.75
      }
   },
   "process_number": 4,
   "meshlab":{
     "path": "/usr/bin/"
   }
}
```

<img src=images/fabscan-dimensions.png>