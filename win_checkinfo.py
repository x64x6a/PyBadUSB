'''
This script could be used to check a USB device's chipset.
It should work if the device is Phison(?)
'''
import sys
from pybadusb import badusb, phison

def print_info(device):
	info  = "Chip type: %04X\n" % device.chip_type
	info += "Chip ID:   %s\n" % device.chip_id
	info += "Version:   %d.%d.%d\n" % device.version
	info += "Mode:      %s\n" % device.run_mode
	print info

if __name__ == '__main__':
	
	# If your USB devices start at 'H'
	device_letter = 'H' if  len(sys.argv) < 2 else sys.argv[1]
	
	#device = badusb.find_drive(phison.Phison2303)
	device = badusb.get_device(phison.Phison2303, device_letter)
	
	if not device:
		print "Device not found"
	elif not device.get_info():
		print "Failed getting info"
		device.close()
	else:
		print_info(device)
		device.close()
