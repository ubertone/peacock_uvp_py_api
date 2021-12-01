# -*- coding: UTF_8 -*-
import unittest
# Add path to the lib folder
import sys, os
lib_path = os.path.abspath(__file__).split('/peacock_uvp_py_api')[0]+'/peacock_uvp_py_api'
sys.path.insert(0, lib_path)
#-------------------------------------

from time import sleep, time
import pathlib
import json

# import modules
from peacock_uvp.apf04_driver import Apf04Driver
from peacock_uvp.apf04_measures import extract_measures

# The main test class
class TestApf04Handler(unittest.TestCase):

	def test_basic_behavior(self):
		# Get settings file path
		model_path = str(pathlib.Path(__file__).parent.absolute()) \
			+ '/test_apf04_json_models'
		assert (os.path.exists(model_path))
		# Read settings file
		with open(model_path+'/settings.json') as json_file:
			settings = json.loads(json_file.read())
			#print ("#### Settings from file :")
			#print(json.dumps(settings, indent=4, sort_keys=True))

		# Create an instance of the Peacock's driver (with 750000/230400/57600 BAUD rate)
		apf_instance = Apf04Driver(230400, 36e6)
		# Read the firmware version
		apf_instance.read_version()

		# Create ConfigHw instance with the first configuration (id = num1) 
		config = apf_instance.new_config()
		config.set(settings["configs"]["num1"])

		#config["method"]+= 2048

		print ("#### Config in human readable format:")
		print(json.dumps(config.to_dict(1480.0), indent=4, sort_keys=True))
		print ("#### Config in hardware format:")
		config.print_config_hw()
		

		# Stop any current action (in case of)
		apf_instance.act_stop()

		# Load the first acoustic configuration into the device
		print("\n\nwrite_config ...")
		apf_instance.write_config (config, 0)

		# select the first acoustic configuration (active config)
		print("select_config ...")
		apf_instance.select_config(0)
		# check the parameters of the active configuration
		print("check_config ...\n\n")
		apf_instance.act_check_config()

		# Read the first acoustic configuration back from the device 
		print ("#### Checked config in human readable format:")
		print(json.dumps(config.to_dict(1480.0), indent=4, sort_keys=True))
		print ("#### Checked config in hardware format:")
		config.print_config_hw()

		# Set the sound speed of the liquid (no automatic sound speed 
		#   calculation)
		print("\n\nsound speed")
		apf_instance.write_sound_speed(1480, False)
		
		# Get measurement duration in order to define the timeout 
		timeout = config.get_bloc_duration()
		print ("timeout = %f"%timeout)

		# Repeat 10 profiles measurements
		count = 10
		startTs = time()
		for _ in range (count):
			# Trigger the measurement of one profile, the function is released
			#   when the data are ready
			apf_instance.act_meas_profile(0.2 + 1.1*timeout)
			# Read the profile data (velocities, echo amplitudes ...)
			raw_us_data = apf_instance.read_profile(config.n_vol)
			us_data = extract_measures(raw_us_data, config)

			print("time = ", us_data["timestamp"].strftime("%Y-%m-%dT%H:%M:%S.%f"))
			print (us_data["velocity"])
			#print (us_data["snr"])


		stopTs = time()
		timeDiff = stopTs  - startTs
		print ("for %d profiles : %f sec"%(count, timeDiff))


# We need this to be able to run the tests outside a test framework.
if __name__ == '__main__':
	unittest.main()
