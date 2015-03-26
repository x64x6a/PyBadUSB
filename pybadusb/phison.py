import sys
import scsi
import struct
from time import sleep

_BOOTROM = "BROM"
_FWBURNR = "BN"
_HWVERFY = "HV"
_FRMWARE = "FW"

class Phison():
	'''
	Base Phison chipset class.
	'''
	
	def __init__(self, driveLetter):
		self.driveLetter = driveLetter
		self.SCSI_device = scsi.open(r'\\.\%s:' % self.driveLetter)
		
		self.data = None 
		self.version = None
		self.f1f2 = None
		self.date = None
		self.run_mode = 'Unknown'
		self.chip_type = None
		self.chip_id = None
	
	def __enter__(self):
		return self
	
	def __exit__(self, type, value, traceback):
		self.close()
	
	def close(self):
		self.SCSI_device.close()

class Phison2303(Phison):
	'''
	Object used to communicate with the Phison2303 chipset.
	'''
	def get_mode(self):
		'''
		Similar to get_info, except only sets run_mode
		'''
		self.data = self.SCSI_device.read('\x06\x05\x00\x00\x00\x00\x00\x00\x01',528)
		
		if not self.data or self.data[0x17A:0x17C]!='VR':
			return False
		
		if self.data[0xA0:0xA8]==' PRAM   ':
			self.run_mode = _BOOTROM
		elif self.data[0xA0:0xA8]==' FW BURN':
			self.run_mode = _FWBURNR
		elif self.data[0xA0:0xA8]==' HV TEST':
			self.run_mode = _HWVERFY
		else:
			self.run_mode = _FRMWARE
		return True
	
	def get_info(self):
		'''
		Performs a SCSI call to read version info from the device.
		Returns bool.
		
		The object's following attributes are set:
			data, version, run_mode, chip_type, date, f1f2
		'''
		self.data = self.SCSI_device.read('\x06\x05\x00\x00\x00\x00\x00\x00\x01',528)
		
		if not self.data or self.data[0x17A:0x17C]!='VR':
			return False
		
		self.version = struct.unpack('BBB', self.data[0x94:0x97])
		self.f1f2 = struct.unpack('BB', self.data[0x9A:0x9C])
		self.date = struct.unpack('BBB', self.data[0x97:0x9A])
		
		if self.data[0xA0:0xA8]==' PRAM   ':
			self.run_mode = 'BROM'	# BootROM
		elif self.data[0xA0:0xA8]==' FW BURN':
			self.run_mode = 'BN'		# firmware burner
		elif self.data[0xA0:0xA8]==' HV TEST':
			self.run_mode = 'HV'		# hardware verify
		else:
			self.run_mode = 'FW'		# firmware
		
		self.chip_type = struct.unpack('>H', self.data[0x17E:0x180])[0]
		
		data = self.SCSI_device.read('\x06\x56\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',512)[0:6].encode('hex').upper()
		self.chip_id = '-'.join(data[i:i+2] for i in range(len(data))[::2])
		
		return True
	
	def load_file(self, firmware, hdr='\x03', bdy='\x02', isFirmware=False):
		'''
		Loads given firmware. Returns bool.
		'''
		# TODO:  fix the issue resolving size.. isFirmware=False is temp solution...
		
		header = firmware[:0x200]
		firmware = firmware[0x200:]
		if header[0:8] != 'BtPramCd':
			raise Exception('Not a Phison image file')
		
		if isFirmware:
			#size = len(firmware) - 512
			size = 204800 # size of firmware images (?)
		else:
			size = struct.unpack('<L', header[0x10:0x14])[0]
			size *= 0x400 # burner size is in 1k pages
		
		# send header
		if not self.SCSI_device.write('\x06\xB1'+hdr+'\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00', header):
			return False
		
		# get header response
		resp = self.SCSI_device.read('\x06\xB0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 8)
		if not resp or resp[0]!='\x55':
			sys.stderr.write('Header not accepted\n')
			return False
		
		# send body
		addr = 0
		while size>0:
			if size>0x8000:
				chunk_size = 0x8000
			else:
				chunk_size = size
			
			cmd_addr = addr >> 9;
			cmd_chunk = chunk_size >> 9;
			if not self.SCSI_device.write('\x06\xB1'+bdy+struct.pack('>HHH', cmd_addr, 0, cmd_chunk)+'\x00\x00\x00\x00\x00\x00\x00', firmware[:chunk_size]):
				sys.stderr.write('Sending body was unsuccessful\n')
				return False
			firmware = firmware[chunk_size:]
			
			resp = self.SCSI_device.read('\x06\xB0\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 8)
			if not resp or resp[0]!='\xA5':
				sys.stderr.write('Body not accepted\n')
				return False
			addr += chunk_size
			size -= chunk_size
		return True
	
	def execute_image(self, firmware):
		'''
		Loads given firmware and runs it.  Returns bool.
		'''
		if not self.load_file(firmware): return False
		if not self.pram(): return False
	
	def run_firmware(self, firmware):
		'''
		Loads firmware onto device.  Returns bool.
		'''
		# rebooting
		self.brom()
		sleep(2)
		
		# sending firmware
		self.load_file(firmware,'\x01','\x00', isFirmware=True)
		ret = self.SCSI_device.read('\x06\xEE\x01\x00\x00\x00\x00\x00\x00', 72)
		sleep(2)
		self.load_file(firmware,'\x03','\x02', isFirmware=True)
		self.SCSI_device.read('\x06\xEE\x01\x01\x00\x00\x00\x00\x00', 72)
		self.SCSI_device.read('\x06\xEE\x00\x00\x00\x00\x00\x00\x00', 72)
		self.SCSI_device.read('\x06\xEE\x00\x01\x00\x00\x00\x00\x00', 72)
		
		# executing
		self.brom()
		sleep(2)
		return True
	
	def pram(self):
		'''
		Called to run a burner or firmware.  Returns int result.
		'''
		return self.SCSI_device.write('\x06\xB3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', '')
	
	def brom(self):
		'''
		Sets device into boot mode from firmware mode.   Returns int result.
		'''
		return self.SCSI_device.write('\x06\xBF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', '')

__all__ = ['Phison', 'Phison2303']
