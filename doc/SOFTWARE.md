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
apt-get install fabscanpi-server opencv-tbb python-serial python-pykka python-picamera avrdude
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
