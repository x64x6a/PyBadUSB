#PyBadUSB
PyBadUSB was created to implement BadUSB on a Phison 2303 device using Python.
The project was inspired by [adamcaudill/Psychson](https://github.com/adamcaudill/Psychson) and [flowswitch/phison](https://bitbucket.org/flowswitch/phison).

The python module ```pybadusb``` is used to communicate with a specified USB device.

##Requirements
* Python 2.7
* Windows or Linux environment

###Firmware
The base firmware you can use is in [bin/fw.bin](bin/fw.bin).
You can compile your own [here](https://github.com/adamcaudill/Psychson/tree/master/firmware).

The burner image used is in [bin/BN03V114M.BIN](bin/BN03V114M.BIN).
Links for finding your own burner image:
* [usbdev](http://www.usbdev.ru/files/phison/)
* [More info](https://github.com/adamcaudill/Psychson/wiki/Obtaining-a-Burner-Image)

###Rubber Ducky
PyBadUSB is currently only designed to embed compiled USB Rubber Ducky scripts.  The test script used can be found in [rubberducky/keys.txt](rubberducky/keys.txt).

You may create your own according to the [Rubber Ducky format](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript) or use one of [these](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Payloads).

Use [DuckEncoder](https://code.google.com/p/ducky-decode/downloads/detail?name=DuckEncoder_2.6.3.zip&can=2&q=) to compile your script:
```
java -jar encoder.java -i keys.txt -o inject.bin
```
The created binary can then be embedded into the base firmware.  See example code below.

###Phison Device
This project has only been developed to work with USB devices with the Phison 2303 chipset.

It doesn't seem to be documented which USB devices use the chipset, but a list of devices may be found on the [Psychson wiki](https://github.com/adamcaudill/Psychson/wiki/Known-Supported-Devices).

If you are looking for a device, it should be noted that the Phison 2303 chipset is only for USB3.0.
It should also be noted that this project will not work with USB2.0 or lower because they do not use SCSI commands.
More info on this can be found [here](http://en.wikipedia.org/wiki/USB_Attached_SCSI).

The [checkchipinfo](checkchipinfo.py) script may also be of use to you.

##Installation
Run the setup script:
```
python setup.py install
```

##Example Code
Here's some example code to get you started:
```python
from pybadusb import badusb, phison

# Set firmware file names
payload  = 'rubberducky/inject.bin'
firmware = 'bin/fw.bin'
burner   = 'bin/BN03V114M.BIN'
embedded = 'hid.bin'

# Finds USB device starting at 'G'
device = badusb.find_drive(phison.Phison2303)

# Linux method:
#device = badusb.get_device(phison.Phison2303, '/dev/sg2')

# Embed firmware
badusb.embed(payload, firmware, embedded)

# Flash new firmware using burner image
badusb.burn_firmware(device, burner, fwfile=firmware)

# Finished
device.close()
```
Another example can be found in [example.py](example.py)

##Module
The Python module is split up into three files:
* [badusb](pybadusb/badusb.py)
  - Used to embed firmware and burn firmware to a device.
* [phison](pybadusb/phison.py)
  - Used to create SCSI commands for the device to get info, burn firmware, etc.
* [scsi](pybadusb/src/scsi.cpp)
  - Used to send SCSI commands to the device
  - Written in C++ as an extension module

