from setuptools import setup
from setuptools import Extension

setup(	name='pybadusb',
		version='0.2',
		packages=['pybadusb'],
		ext_package='pybadusb',
		ext_modules=[Extension('scsi', ['pybadusb/src/scsi.cpp'], extra_compile_args = ["-Wno-write-strings"])],
	)
