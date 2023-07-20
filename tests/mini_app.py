# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer

# Add path to the lib folder
import sys, os
lib_path = os.path.abspath(__file__).split('/peacock_uvp_py_api')[0]+'/peacock_uvp_py_api'
sys.path.insert(0, lib_path)
#-------------------------------------

from time import time
import pathlib
import json
from struct import pack
import re
import logging
logging.basicConfig(level=logging.INFO)

# import modules
from peacock_uvp.apf04_driver import Apf04Driver
from peacock_uvp.apf04_addr_cmd import get_addr_dict
from peacock_uvp.apf_type import cast_int16

from file_handler import FileHandler


def translate_key_to_index(_config_key):
	""" @brief translate config key to index
	@return index (int)
	get index [0..N-1] of config ref ['num1'..'numN']
	extract the number in the key and subtract 1 to get the index starting at 0 
	(from webui2)
	"""
	return int(re.search( r"(\d+)", _config_key).groups(0)[0])-1

def read_json_file(_filename):
	# open and read file
	with open(_filename) as json_file:
		return json.loads(json_file.read())
	
def write_json_file(_filename, _dict):
	# open and write file
	with open(_filename, 'w') as json_file:
		return json_file.write(json.dumps(_dict, indent=4, sort_keys=True))


#####    Get settings and const files   #####
model_path = str(pathlib.Path(__file__).parent.absolute()) + '/mini_app'
assert (os.path.exists(model_path))
settings = read_json_file (model_path+'/settings.json')
#print ("#### Settings from file :")
#print(json.dumps(settings, indent=4, sort_keys=True))
ref = hash(json.dumps(settings))

# Read const file
const = read_json_file (model_path+'/const.json')


#####    Create an instance of the Peacock's driver    #####    
  # Baud rate : 750000/230400/57600
  # system frequency :  36e6/18e6
apf_instance = Apf04Driver(const["hardware"]["baudrate"], const["hardware"]["f_sys"])
apf_instance.addr = get_addr_dict(apf_instance.read_version()[1])
# Read the firmware version
apf_instance.read_version()

const["serial_num"]="%2d%04d"%(apf_instance.year-2000, apf_instance.serial_num)
# create product id (keep only alpha chars from product_model) 
const["product_id"]= ''.join(filter(str.isalnum, const["product_model"])).lower() + const["serial_num"]

const["hardware"]["firmware_version"] = "%s"%apf_instance.version_c
const["hardware"]["logic_version"] = "%s"%apf_instance.version_vhdl


#####    Set acoustic configuration    #####
sound_speed = settings["global"]["sound_speed"]["value"]
print ("Sound speed set by user : %.1f m/s"%sound_speed)
# dict for hardware style configurations 
settings_hw={}
# Create ConfigHw instance with the first configuration (id = num1) 
config_hw = apf_instance.new_config()
## TODO for config in settings["configs"] :
config_hw.set(settings["configs"]["num1"]) #TODO manage blind zone
settings_hw["num1"] = config_hw

print ("#### Config in human readable format:")
print(json.dumps(config_hw.to_dict(sound_speed), indent=4, sort_keys=True))
print ("#### Config in hardware format:")
config_hw.print_config_hw()

# Stop any current action (in case of)
apf_instance.act_stop()

# Load the first acoustic configuration into the device
print("\n\nwrite_config ...")
apf_instance.write_config (config_hw, 0) # TODO incrémenter dans loop

# select the first acoustic configuration (active config)
print("select_config ...")
apf_instance.select_config(0) # TODO translate_key_to_index("num1")
# check the parameters of the active configuration
print("check_config ...\n\n")
apf_instance.act_check_config()

# Read the first acoustic configuration back from the device 
print ("#### Checked config in human readable format:")
print(json.dumps(config_hw.to_dict(sound_speed), indent=4, sort_keys=True))
print ("#### Checked config in hardware format:")
config_hw.print_config_hw()

# update settings dict with effective config
settings['configs']['num1'] = config_hw.to_dict(sound_speed)
# update settings.json
write_json_file(model_path+'/settings.json', settings)

# Set the sound speed of the liquid (no automatic sound speed 
#   calculation)
print("\n\nsound speed")
apf_instance.write_sound_speed(int(sound_speed), False)

# Get measurement duration in order to define the timeout 
# TODO attention, get_bloc_duration n'est pas exact, reprendre dans webui2 / apf_rules / compute_info()
timeout = config_hw.get_bloc_duration()
print ("timeout = %f"%timeout)

raw_file = FileHandler(const)
raw_file.write_settings(settings, settings_hw)


# Acquire 50 profiles 
count = 50
startTs = time()
for _ in range (count): # TODO loop on configs
	# Trigger the measurement of one profile, the function is released
	#   when the data are ready
	apf_instance.act_meas_profile(0.2 + 1.1*timeout)
	# Read the profile data (velocities, echo amplitudes ...)
	raw_us_data = apf_instance.read_profile(config_hw.n_vol)

	# Add the settings ref and config id to the raw profile.
	# (config id is 0 when config key is num1)
	raw_data = pack("h", cast_int16((ref & 0x000007FF) << 4 | translate_key_to_index("num1")))
	# Read the measured profiles and add them to the raw data.
	raw_data += apf_instance.read_profile(settings_hw["num1"].n_vol)

	raw_file.write_profile(raw_data)


stopTs = time()
timeDiff = stopTs  - startTs
print ("for %d profiles : %f sec"%(count, timeDiff))

raw_file.close()
