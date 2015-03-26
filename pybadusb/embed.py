import sys

def embed(payload, firmware, outfile=None):
	'''
	embed(payload, firmware, outfile) -> Embeds payload in within firmware and stores it as outfile
	embed(payload, firmware) -> Embeds payload in within firmware and returns the raw data
	'''
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

__all__ = ['embed']