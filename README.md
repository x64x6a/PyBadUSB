#PyBadUSB
This project was created to implement BadUSB on a device using python.  It was based off of code and ideas from [adamcaudill/Psychson](https://github.com/adamcaudill/Psychson) and [flowswitch/phison](https://bitbucket.org/flowswitch/phison).

It contains the python module ```pybadusb``` which is used to communicate with a USB device.

##Requirements
* Python 2.7.9
* Windows environment

#Firmware
The base firmware you can use is in [bin/fw.bin](bin/fw.bin).
You can compile your own [here](https://github.com/adamcaudill/Psychson/tree/master/firmware).

The burner image used is in [bin/BN03V114M.BIN](bin/BN03V114M.BIN).
Links for finding your own burner image:
*(usbdev)[http://www.usbdev.ru/files/phison/]
*(More info)[https://github.com/adamcaudill/Psychson/wiki/Obtaining-a-Burner-Image]

#Rubber Ducky
Testing was only performed with USB Rubber Ducky scripts.  The used test script can be found in (rubberducky/keys.txt)[rubberducky/keys.txt].

You may create you own according to the Rubber Ducky format or use one of [these](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Payloads).

Use (DuckEncoder)[https://code.google.com/p/ducky-decode/downloads/detail?name=DuckEncoder_2.6.3.zip&can=2&q=] to compile your script:
```
java -jar encoder.java -i keys.txt -o inject.bin
```
The created binary can then be embedded into the base firmware.  See example code below.

##Example Code
```python
from pybadusb import badusb, phison

# Set firmware file names
payload  = 'rubberducky/inject.bin'
firmware = 'bin/fw.bin'
burner   = 'bin/BN03V114M.BIN'
embedded  = 'hid.bin'

# Finds USB device starting at 'G'
device = badusb.findDrive(phison.Phison2303)

# Embed firmware
badusb.embed(payload, firmware, embedded)

# Flash new firmware using burner image
badusb.burn_firmware(device, burner, fwfile=firmware)

# Finished
device.close()
```
Another example can be found in ```example.py```

##Module
The module is split up into three parts:
*badusb
  -Used to embed firmware and burn firmware to a device.
*phison
  -Used to create SCSI commands for the device to get info, burn firmware, etc.
*scsi
  -Used to send SCSI commands to the device
  -Written in C++, code can be found in (src/scsimodule.cpp)[src/scsimodule.cpp]

##Known Phison2303 Chipset Devices
There is a list [here](https://github.com/adamcaudill/Psychson/wiki/Known-Supported-Devices)
