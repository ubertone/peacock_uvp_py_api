# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer

from os import listdir, path, remove, fstat
from time import strftime
from datetime import datetime
from struct import pack, calcsize
from json import dumps
import logging
logging.basicConfig(level=logging.DEBUG)

PROFILE_TAG = 100
CONFIG_TAG = 200
SETTINGS_JSON_TAG = 201
CONST_TAG = 300

# \brief raw record file.
# (from webui2)
class FileHandler():

	# \brief The directory where we will record the data
	RECORD_DIRECTORY = 'record'

	def __init__(self, _const):
		"""
		@brief Create an UbtFileHandler instance
		"""

		# Get timestamp as string
		datetime_timestamp = strftime("%Y%m%d_%H%M%S", datetime.now().timetuple())

		# Create .udt file with timestamp.
		self.filename = "raw_" + datetime_timestamp + ".udt"
		self.handler = open( self.RECORD_DIRECTORY + "/" + self.filename, 'wb')

		header = 'UDT005' + ' ' \
			+ _const["hardware"]["board_version"] + ' ' \
			+  _const["software"]["version"] + '/' +  _const["hardware"]["firmware_version"] + '/' +  _const["hardware"]["logic_version"]
		
		logging.debug("header = '%s'"%(header) )
		self.handler.write('{:\0<42}'.format(header).encode('ascii')) 

		self.__write_const__(_const)


	def size(self):
		"""
		Donne la taille courante du fichier sur le disque
		"""
		#self.profiler_start()
		filesize = fstat(self.handler.fileno()).st_size
		#self.profiler_stop("fstat file")
		logging.debug ("filesize is %d"%filesize)
		return filesize


	def __write_const__(self, _const):
		"""
		@brief Write const in raw record file
		"""

		logging.debug("record const")
		#### Writing the Json ####
		const_json = dumps(_const)
		logging.debug("const : \n-----------\n%s\n-----------\n"%const_json)

		chunk_size = len(const_json)

		# Config to chunk (size is given in number of bytes)
		logging.debug("const len : %d / type : %s"%(chunk_size, type(const_json)))
		config_header = pack("hh", CONST_TAG, chunk_size * calcsize ('c'))
		config_chunck = pack('%ds'%(chunk_size), const_json.encode('utf8'))

		# Write chunk in file
		self.handler.write(config_header+config_chunck)


	def write_settings(self, _settings, _settings_hw):
		"""
		@brief Write settings in raw record file
		"""

		logging.debug("record settings")
		#### Writing the Json ####
		settings_json = dumps(_settings)
		logging.debug("settings : \n-----------\n%s\n-----------\n"%settings_json)

		chunk_size = len(settings_json)

		# Config to chunk (size is given in number of bytes)
		logging.debug("settings len : %d / type : %s"%(chunk_size, type(settings_json)))
		config_header = pack("hh", SETTINGS_JSON_TAG, chunk_size * calcsize ('c'))
		config_chunck = pack('%ds'%(chunk_size), settings_json.encode('utf8'))
		# https://stackoverflow.com/questions/21726324/using-struct-pack-with-strings

		# Write chunk in file
		self.handler.write(config_header+config_chunck)
		

		#### Writing the config HW ####
		# For each config in settings:
		for config_key in _settings['global']['configuration_order']:
			# Read hardware config in data
			config_list = _settings_hw[config_key].to_list()
			config_hw_size = len(config_list)

			# Config to chunk (size is given in number of bytes)
			config_header = pack("hh", CONFIG_TAG, config_hw_size * calcsize ('h'))
			config_chunck = pack("%dh"%config_hw_size, *config_list)

			# Write chunk in file
			self.handler.write(config_header+config_chunck)


	def write_profile(self, _raw_data):
		"""
		@brief  Write a profile in raw record file
		@param _profile profile to record in raw file
		"""
		# Prepare the header
		header = pack("hh", PROFILE_TAG, len(_raw_data))
		# Write the header and the profile measured
		self.handler.write(header + _raw_data)


	def close(self):
		"""
		@brief Close the file(s) associated to the handler
		"""
		#self.handler.write("test")
		self.handler.close()
