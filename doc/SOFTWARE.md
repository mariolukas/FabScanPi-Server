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
