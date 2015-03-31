from distutils.core import setup
from distutils.extension import Extension

setup(	name='pybadusb',
		version='0.1',
		packages=['pybadusb'],
		ext_package='pybadusb',
		ext_modules=[Extension('scsi', ['pybadusb/src/scsi.cpp'])],
	)
