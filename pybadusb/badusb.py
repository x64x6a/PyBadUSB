import sys

_BOOTROM = "BROM"
_FWBURNR = "BN"
_HWVERFY = "HV"
_FRMWARE = "FW"

def embed(payload_file, fwfile, outfile=None):
	'''
	embed(payload_file, fwfile, outfile) -> Embeds payload in within firmware and stores it as outfile
	embed(payload_file, fwfile) -> Embeds payload in within firmware and returns the raw data
	'''
	with open(payload_file, 'rb') as f:
		payload = f.read()
	with open(fwfile, 'rb') as f:
		firmware = f.read()
	
	header = firmware[:0x200]
	data = firmware[0x200:]
	
	signature = '\x12\x34\x56\x78'
	found = False
	for i in range(len(data)):
		if data[i:i+len(signature)] == signature:
			found = True
			address = i
			break
	if not found:
		sys.stderr.write('Signature not found\n')
		return False
	
	if  address+0x200 >= 0x6000:
		raise Exception('Insufficient memory to inject file')
	
	out  = header + data[:address] 
	out += payload + data[address+len(payload):]
	if outfile:
		with open(outfile, 'wb') as f:
			f.write(out)
		return True
	else:
		return out

def burn_firmware(device, burner_file, fwfile=None, firmware=None):
	'''
	burn_firmware(device, burner_file, fwfile) -> Burns firmware to device using burner.
	burn_firmware(device, burner_file, firmware=firmware) -> Burns firmware string to device using burner.
	'''
	if not fwfile and not firmware:
		raise Exception("Invalid Parameters")
		return False
	
	# read from fwfile
	if fwfile:
		with open(fwfile, 'rb') as f:
			firmware = f.read()
	
	with open(burner_file, 'rb') as f:
		burner = f.read()
	
	if device.run_mode != _FWBURNR:
		if device.run_mode != _BOOTROM:
			device.brom()
		if not device.execute_image(burner):
			return False
	return device.run_firmware(firmware)

def embed_burn(device, payload_file, fwfile, burner_file):
	'''
	embed_burn(device, payload_file, fwfile, burner_file) -> embeds payload into firmware and then burns to device.
	'''
	new_firmware = embed(payload_file, fwfile)
	if not new_firmware: return False
	return burn_firmware(device, burner_file, firmware=new_firmware)

def find_drive(device_type, start='E', end='P'):
	'''
	findDrive(device_type, start='E', end='P') -> attempts to create a new device_type starting at drive 'E' and ending at 'P'
	'''
	for i in range(ord(start), ord(end)):
		device = device_type(chr(i))
		if device.SCSI_device:
			return device
	return False

def get_device(device_type, letter):
	'''
	getDevice(device_type, letter) -> creates a new device_type with drive letter.
	
	Returns False on failure.
	'''
	device = device_type(letter)
	if device.SCSI_device:
		return device
	return False

__all__ = ['embed', 'burn_firmware', 'embed_burn', 'find_drive', 'get_device']