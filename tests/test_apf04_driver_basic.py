# -*- coding: UTF_8 -*-
import unittest
# Add path to the lib folder
import sys, os
lib_path = os.path.abspath(__file__).split('/peacock_uvp_py_api')[0]+'/peacock_uvp_py_api'
sys.path.insert(0, lib_path)
#-------------------------------------

import logging
logging.basicConfig(level=logging.DEBUG)

# import modules
from peacock_uvp.apf04_driver import Apf04Driver

# The main test class
class TestApf04Driver(unittest.TestCase):

	def test_basic_behavior(self):
		# Create an instance of the Peacock's driver (with 230400/57600  BAUD rate)
		apf_instance = Apf04Driver(230400, 36e6)

		# Read the firmware version
		vhdl_v, c_v = apf_instance.read_version()
		print("vhdl: %d, c: %d"%(vhdl_v, c_v))

		print("Firmware version : %s"%apf_instance.read_buf_i16(0, 3))
		print ("---------------------------------------------")

		# Read the default configuration stored in the Peacock UVP device :
		print(apf_instance.read_config(0).to_dict(1480.0))

		# Read the pitch on embedded sensor :
		print ("pitch: %s"%(apf_instance.read_pitch()))

		# Run the LED blinking
		print (" *************  acting LED *****************")
		apf_instance.act_test_led()

		print (" *************  Test Read / Write *****************")
		# Basic memory read / writ operations
		apf_instance.set_timeout(4)
		apf_instance.write_buf_i16(range(60), 4)
		echo_data = apf_instance.read_buf_i16(4, 60)
		print (echo_data)
			

# We need this to be able to run the tests outside a test framework.
if __name__ == '__main__':
	unittest.main()
