# -*- coding: UTF_8 -*-

import unittest
# Add path to the lib folder
import sys, os
lib_path = os.path.abspath(__file__).split('/peacock_uvp_py_api')[0]+'/peacock_uvp_py_api'
sys.path.insert(0, lib_path)
#-------------------------------------


from peacock_uvp.apf04_gain import convert_code2dB, convert_dB2code


# The main test class
class TestGain(unittest.TestCase):
	def test_gain_convertion(self):
		print ("### test gain conversion :")
		for gc in range(10, 1250, 10):
			gdb = convert_code2dB(gc)

			print ("\tG =%.2f dB <-> code %d " % (gdb, gc))

			# check the opposit function 
			assert (int(convert_dB2code(gdb)) == gc) 

		
# We need this to be able to run the tests outside a test framework.
if __name__ == '__main__':
	unittest.main()