from setuptools import setup
from setuptools import Extension
import platform

if platform.system() == 'Windows':
	scsi_compile_args = []
else:
	scsi_compile_args = ["-Wno-write-strings"]


setup(	name='pybadusb',
		version='1.0',
		package_dir = {'': 'src'},
		packages=['pybadusb'],
		ext_package='pybadusb',
		ext_modules=[Extension('scsi', ['src/scsi.cpp'], extra_compile_args = scsi_compile_args)],
	)
