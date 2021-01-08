# -*- coding: UTF_8 -*-

# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.

import unittest
# Add path to peacock_uvp_py_api folder for accessing to the modules
import sys, os
webui_path = os.path.abspath(__file__).split('/peacock_uvp_py_api')[0]+'/peacock_uvp_py_api'
sys.path.insert(0, webui_path)
#-------------------------------------

import time
import logging

from peacock_uvp.apf04_modbus import Apf04Modbus as modbus


def hex_print (_bytes):
	print (''.join('%02x'%i for i in _bytes))

baudrate = 230400
logging.basicConfig(level=logging.DEBUG)

# The main test class
class TestApf04Modbus(unittest.TestCase):
	def test1_readseg(self):
		apf = modbus(baudrate) # , "/dev/tty.usbserial-FTWVIUZU"

		print ("\nTest read basic segment")
		start = time.time()
		resp = apf.read_seg_16(0, 4)
		end = time.time()
		print("full request time : %f"%(end - start))

		hex_print(resp)
	
	def test2_readi16(self):
		apf = modbus(baudrate)

		print ("\nread 1 value at 0 : ")
		version = apf.read_i16(0)
		print (type(version))
		
		print(version)

		print ("*************************")

		print ("read 1 value at 0xFFFE : ")
		print(apf.read_i16(0xFFFE))
		

	def test2_writeseg(self):
		apf = modbus(baudrate)

		start = time.time()
		apf.write_buf_i16(range(5), 4)
		end = time.time()
		print("full request time : %f"%(end - start))

		resp = apf.read_seg_16(4, 5)
		end = time.time()
		print("full request time : %f"%(end - start))

		hex_print(resp)

	def test3_readbuf(self):
		apf = modbus(baudrate)

		start = time.time()
		apf.write_buf_i16(range(70), 4)
		end = time.time()
		print("full request time : %f"%(end - start))

		start = time.time()
		resp = apf.read_buf_i16(0, 300)
		end = time.time()
		print("full request time : %f"%(end - start))

		hex_print(resp)

	def test3_write_error(self):
		apf = modbus(baudrate)

		start = time.time()
		apf.write_buf_i16(range(100), 4)
		end = time.time()
		print("full request time : %f"%(end - start))
	
	def test4_autobaud(self):
		apf = modbus()
		baudrate = apf.autobaud()
		if not baudrate:
			print ("##########################Autobaud failed, try again")
			baudrate = apf.autobaud()


		print ("########### detected baurate = %d\n"%baudrate) 

		
# We need this to be able to run the tests outside a test framework.
if __name__ == '__main__':
	unittest.main()