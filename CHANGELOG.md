# FabScanPi - Open Source 3D Scanner Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [0.9.0] - unreleased

### TODO
- migrate python 2 to python 3
- refactor serial driver make it more abstract to general connector interface
- add connector for GPIO's
- support for cricket board

### Added

### Changed

### Fixed

## [0.8.1] - unreleased

### Added

### Changed

### Fixed
- update routine


## [0.8.0] - 2019-08-11

### Added
- temperature watch dog
- support for second laser
- ciclop and clones support ( interleaved image option )
- new firmware for cncboard, ciclop and fabscan shield
- new version of frontend with some bugfixes (see frontend repository)
- scanning with multiple lasers saves multiple pointclouds now, one for each
  laser and one merged. 
- saving raw images for photogrammetry.
- added firmware for ciclop, cncshield and snguinololu board

### Changed
- default config file, added new params and settings
- arduino firmware builds with arduino cli and make file now
- switched docs from md to rst
- fixed build process
- added support to save images, texture and laser 
- zipping images 

### Fixed
- communication with external hardware over serial (arduino, FabScanPi HAT)
- high res out of memory bug
- prevent async steps while calibration and scanning 
- stepper blocking mode
- hardware connection check while server is starting (waking up the conttoller)
- removed bootloader form firmware to prevent flashing damages
- fixed long timeouts while connecting to the client when no internet conneciton is availanel (aka cccamp bug)

 
## [0.7.0] -  2019-02-21
### Added
- new settings dialog options for hardware contolling
- moved calibration button to settings dialog
- added new configuraitons in general settings tab
- prepared platform independet firmware setup (aka cyclop compatible mode)
- api route for live log stream
- api route for debug log zip download
- new firmware version
- made fabscan discoverable in find.fabscan.org
- apscheduler library for registery servcie and future scheduling tasks
- added meshmixer to package dependencies
- added avrdude config to package dependencies

### Changed
- replaced old image build script by a new one, based on  official raspbian build scripts
- FSUpdate is working for different stages now

### Fixed
- fixed camera driver (pi and usb)
- fixed random artifacts at the beginning of object scan

## [0.6.0] - 2018-11-23
### Added 
- introduced Tornado Web Framework
- added new version of frontend with some fixes
- added swapping support for high res scans
- added new refactored firmware v.20181123
 
### Changed
- refactored Websocket Server
- refactored Web Server
- refactored Streaming Handler
- refactored project structure

### Fixed
- Turntable Blocking mode
- Image Ring Buffer Flushing
- removed random artifacts at the beginning of object scan
- stepper missing steps bug (aka stepper wobble)
- avrdude bug
- gap at the beginning/end of a scan

## [0.5.0] - 2018-04-04
### Added
- new documentation parts (tnx to jens hackel)
- added stop sequence when scanner is not calibrated
- added new handlers for gracefull application shutdown
- added toast message at the end of calibration if calibration failed

### Changed
- replaced magic numbers by config values (tnx to jwalt)
- refactored camera driver ( much faster than before )
- removed dead code

### Fixed
- fixed pykka aktor threading bug in streams
- fixed typo in documentation (tnx to kradrat)
- fixed green cam bug
- fixed stepper motors step bug (variable number of steps should work now)
- deleting old calibration data before new calibration
- fixed update procedure, added assume yes option
- fixed start stop init script and added better logging to it

## [0.4.3] - 2017-07-26
### Added
- new meshing file formats (off, 3ds, x3d, xyz...)
- new sections to f.a.q. in docs

### Fixed
- fixed calibration data saving bug
- reworked meshing process and added new mlx filter scripts

## [0.4.2] - 2017-07-10
### Fixed
- fixed update notification bug
- fixed firmware issue which leaded to bricked devices.

## [0.4.1] - 2017-07-2
### Added
- added calibration notification message
  
### Fixed
- fixed preview stream issues
- fixed default config values
- fixed turntable pointcloud roi

## [0.4.0] - 2017-07-2
### Added
- added news to documentation 
- added auto calibration
- added news screen to fabscan server start screen

### Fixed
- first fixes for upgrade
- fixed major bug with serial connection

### Changed
- improved laser line detection


## [0.3.1] - 2016-09-26
### Fixed
- fixed bug which created multiple instances for websocket server
- fixed bug which calculated wrong version numbers in upgrade check

## [0.3.0] - 2016-07-08
### Added
  
- added splash screen to frontend
- added auto upgrade to frontend and backend
- added calibration option to settings dialog

### Fixed
- fixed major laser detection error
- fixed some 3D calculation bugs

### Changed
- refactored core for making it more modular
- simplified the laser settings dialog (threshold values etc.) better preview now

## [0.2.1] - 2016-07-06
### Added
- added new dependencies to control file

### Fixed
- fixed avrdude flashing for FabScan HAT

## [0.2.0] - 2016-03-12
### Added
- added idle spinner to stream preview window
- added meshlab support to frontend
- added calibration stream option
- added meshalabserver support by calling via xvfb
- added new icons
- added system call stdouts to log file
- added version number of firmware and server visible in main window

### Fixed
- fixed issue #5, heavy CPU load
- fixed status bar
- fixed mpjeg close stream bug in chrome and firefox

### Changed
- refactored system callings, introduced new utils for system calls
- prepared frontend for laser stepper support 
- replaced threejs v70 by a newer version v74
- refactored webgl directive, added support for switching between mesh and pointcloud (experimental)
- refactored laser detection algorithm, it is more stable now.
- refactored and extended share dialog options
- refactored httpRequestHandler
- refactored REST api
- replaced angular-slick
- refactored general file handling

## [0.1.15] - 2016-02-25
### Added
- added auto detection for arduino
- added some additional connection messages to frontend
- added override function for bassehttp logger to get cleaner logs

### Fixed
- fixed firmware autoflash bug, it finds the correct hex file now.
- fixed firmware autoflash bug, it finds the correct hex file now.

### Changed
- refactored and cleaned FSSerial.py
- removed serial port from default config

## [0.1.14] - 2016-02-23

### Fixed
- fixed firmware motor reverse issue
- fixed serial connection error for custom arduino installations.

## [0.1.13] - 2016-02-20
### Added
- added new frontend with saturation slider
- added funtions to support camera saturation adjustment
- added multilingual support (en only until now)
- added error handler message to frontend

### Fixed
- fixed issue #12 internet connection is no longer needed, added font-awsome fonts to www
- fixed issue #3 server hangs when laser not detected
- fixed mjepeg connection error bug, stack trace is not longer shown in log
- fixed some bugs in FSCamera.py

## [0.1.12] - 2016-02-10

### Changed
- switched from depricated python-support to dh_python2 package builder
- modified makefile to fit the new builder

## [0.1.11] - 2016-02-10

### Added
- added update instructions do documentation

### Changed
- modified init script

## [0.1.10] - 2016-02-10
## added
- new frontend version

## [0.1.9] - 2016-02-8

### Changed
- fixed debian package installer scripts

## [0.1.8] - 2016-02-8

### Changed
- fixed python package path error

## [0.1.7] - 2016-02-8
### Added
- added auto versioning to setup.py

### Changed
- fixed versioning in frontend
- fixed some camera parameters for better color scan results
- fixed issue #3
- fixed frontend 

## [0.1.6] - 2016-02-4
### Added
- added motor enable/disable commands before and after scans to prevent hot motors

### Changed
- switched to firmware v.20160204 which supports custom boards and fixes some issues

### Fixed
- closed issue #4 added auto flash enable/disable option to config file

## [0.1.5] - 2016-01-15
### Added
- Added new Frontend version.

## [0.1.4] - 2016-01-14
### Fixed
- Fixed frontend

## [0.1.3] - 2016-01-11
### Fixed
- Fixed Firefox mjpeg stream issue
- Fixed pi camera exposure issue

## [0.1.2] - 2016-01-02
### Added
- New User Interface added

## [0.1.1] - 2016-01-02
### Fixed
- scan data folders

## [0.1.0] - 2016-01-02
### Added
- First Release of FabScanPi-Server.

 