#PyBadUSB
This project was created to implement BadUSB on a device using python.  It was based off of code and ideas from [adamcaudill/Psychson](adamcaudill/Psychson) and [flowswitch/phison](https://bitbucket.org/flowswitch/phison).

It contains the python module ```pybadusb``` which is used to communicate with a USB device.

##Requirements
* Python 2.7.9
* Windows environment

##Example
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
