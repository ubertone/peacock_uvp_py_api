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
from peacock_uvp.apf04_addr_cmd import get_addr_dict


# The main test class
class TestApf04Driver(unittest.TestCase):

	def test_basic_behavior(self):
		# Create an instance of the Peacock's driver (with 230400/57600  BAUD rate)
		#apf_instance = Apf04Driver(750000, 36e6)
		#apf_instance = Apf04Driver(230400, 18e6)
		apf_instance = Apf04Driver(57600, 36e6)
		apf_instance.addr = get_addr_dict(apf_instance.read_version()[1])
		#apf_instance.addr = get_addr_dict(addr_json=os.path.abspath(__file__).split('/Python/')[0] + "/Python/webui2/tests/prod_apf04/json/addr_UBFLOWAV.json")
		print(apf_instance.addr)

		# Read the firmware version
		vhdl_v, c_v = apf_instance.read_version()
		print("vhdl: %d, c: %d"%(vhdl_v, c_v))

		print("Firmware version: %s"%apf_instance.read_buf_i16(0, 3))
		print("serial num: %2d%04d"%(apf_instance.year-2000, apf_instance.serial_num))
		print ("---------------------------------------------")

		# Read the default configuration stored in the Peacock UVP device :
		print(apf_instance.read_config(0).to_dict(1480.0))

		# Read the pitch on embedded sensor :
		print ("pitch: %s"%(apf_instance.read_pitch()))

		# Run the LED blinking. WARNING: only available with model 1 (PEACOCK), not 32 (UBFLOWAV)
		print (" *************  acting LED *****************")
		#apf_instance.act_test_led()

		print (" *************  Test Read / Write *****************")
		# Basic memory read / writ operations
		apf_instance.write_buf_i16(range(60), 4, 4.0)
		echo_data = apf_instance.read_buf_i16(4, 60)
		print (echo_data)
			

# We need this to be able to run the tests outside a test framework.
if __name__ == '__main__':
	unittest.main()
