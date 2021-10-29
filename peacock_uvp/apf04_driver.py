#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @copyright  this code is the property of Ubertone. 
# You may use this code for your personal, informational, non-commercial purpose. 
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer

from datetime import datetime
import struct
import logging

from .apf04_modbus import Apf04Modbus
from .apf04_addr_cmd import *
from .apf04_config_hw import ConfigHw
from .apf_timestamp import encode_timestamp

# TODO gérer ici les erreur spécifiques au HW

class Apf04Driver (Apf04Modbus):
	""" @brief gère l'instrument APF04
	"""
	# TODO : tester la com dans un init par une lecture de la version 
	def __init__(self, _baudrate, _f_sys, _dev=None):
		self.f_sys=_f_sys
		Apf04Modbus.__init__(self, _baudrate, _dev)

	def new_config (self):
		"""  @brief create an empty config
		"""
		# TODO pourrait aussi s'appeler create_config ou empty_config @marie : un avis ?
		return ConfigHw(self.f_sys)

	def read_config (self, _id_config=0):
		""" @brief lecture des paramètres d'une configuration
		    @param _id_config : identifiant de la configuration [0..2] (par défaut la config n°1/3) 
				
				principalement utilisé pour relire la config après un check_config
				"""
		self.config = ConfigHw(self.f_sys)
		self.config.id_config = _id_config
		#	tous les paramètres des settings sont en signé
		self.config.from_list(self.read_list_i16(ADDR_CONFIG+_id_config*OFFSET_CONFIG, SIZE_CONFIG)) # en mots
		return self.config
	
	# TODO .to_list() à faire par l'appelant ? APF04Driver ne connait pas config_hw ou passer config_hw en self.config (actuellement au niveau au dessus) ?
	def write_config (self, _config, _id_config):
		""" @brief écriture des paramètres d'une configuration
		    @param _config : configuration (de type ConfigHw)
		    @param _id_config : identifiant de la configuration [0..2]
		"""
		logging.debug("%s"%(_config.to_list()))
		self.write_buf_i16(_config.to_list(), ADDR_CONFIG+_id_config*OFFSET_CONFIG)

	# DEFINI LA CONFIG 0 UTILISEE PAR L'APPAREIL
	# _config = [0..2]
	def select_config (self, _id_config):
		logging.debug("selecting config %d [0..N-1]"%(_id_config))
		self.write_i16(_id_config, ADDR_CONFIG_ID)

	def read_version (self):
		""" @brief Lecture des versions C et VHDL
		"""
		self.version_vhdl = self.read_i16(ADDR_VERSION_VHDL)
		self.version_c = self.read_i16(ADDR_VERSION_C)
		logging.debug("Version VHDL=%s", self.version_vhdl)
		logging.debug("Version C=%s", self.version_c)
		if self.version_c < 45:
			print ("WARNING firmware version %d not supported (version 45 or higher required)" % self.version_c)
		
		model_year = self.read_i16(ADDR_MODEL_YEAR)
		self.model = (model_year & 0xFF00)>>8
		self.year = 2000 + (model_year & 0x00FF)

		if self.model == 0x01 :
			logging.debug("Model is Peacock UVP")
		elif self.model == 0x20 : 
			logging.debug("Model is an UB-Flow AV")
		else :
			logging.info("Warning, model (id %s) is not defined"%self.model)	
		logging.debug("Year of production = %s", self.year)
		
		self.serial_num = self.read_i16(ADDR_SERIAL_NUM)
		logging.debug("Serial number=%s", self.serial_num)
		
		return self.version_vhdl, self.version_c

	def write_sound_speed (self, sound_speed=1480, sound_speed_auto=False):
		""" @brief Writing of the sound speed global parameter in RAM
		"""
		addr_ss_auto = ADDR_SOUND_SPEED_AUTO
		addr_ss_set = ADDR_SOUND_SPEED_SET
		# fix for firmware prior to 45
		if self.version_c < 45:
			addr_ss_auto -= 2
			addr_ss_set -= 2

		if sound_speed_auto:
			self.write_i16(1, addr_ss_auto)
		else:
			self.write_i16(0, addr_ss_auto)
			self.write_i16(sound_speed, addr_ss_set)

	def act_stop (self):
		self.write_i16(CMD_STOP, ADDR_ACTION)

	def act_meas_I2C (self):
		""" @brief Make one measure of pitch, roll and temp. Those values are then updated in the RAM.
		"""
		self.write_i16(CMD_TEST_I2C, ADDR_ACTION)

	def act_test_led (self):
		self.write_i16(CMD_TEST_LED, ADDR_ACTION)
		
	def act_meas_IQ (self):
		self.write_i16(CMD_PROFILE_IQ, ADDR_ACTION)
		
	def act_meas_profile (self, _timeout=0.):
		""" @brief démarrage d'une mesure de profil
		    @param _timeout timeout permettant également de choisir entre mode bloquant (avec timeout) et non-bloquant (timeout à zéro)

				en mode bloquant, la fonction rend la main lorsque la mesure est terminée. Les données sont alors immédiatement disponibles.
				en mode non-bloquant, la fonction rend la main immédiatement. L'appelant devra surveiller le header du profil : 
					lorsque le champ "sound_speed" n'est pas nul, le profil est disponible.
		"""
		# get UTC timestamp just before strating the measurements
		self.timestamp_profile = datetime.utcnow()

#		if _timeout==0.: # mode non bloquant
#			self.set_timeout(0.1)
#			self.write_i16(CMD_PROFILE_NON_BLOCKING, ADDR_ACTION)
#		else:            # mode bloquant
		logging.debug ("setting timeout to %f"%_timeout)
		self.set_timeout(_timeout)
		# TODO san 04/12/2019 voir pour travailler 
		# en bloquant si < 2secondes ;  et non-bloquant + sleep au-delà (permet d'interrompre la mesure sur event stop à passer en argument)

		self.write_i16(CMD_PROFILE_BLOCKING, ADDR_ACTION)
		
		
	def act_check_config (self):
		self.write_i16(CMD_CHECK_CONFIG, ADDR_ACTION)

	def act_start_auto_mode (self):
		self.write_i16(CMD_START_AUTO, ADDR_ACTION)

	def read_temp (self):
		return self.read_i16(ADDR_TEMP_MOY)

	def read_pitch (self):
		return self.read_i16(ADDR_TANGAGE)
		
	def read_profile (self, _n_vol):
		logging.debug("timestamp: %s"%self.timestamp_profile)

		#logging.debug("pitch: %s, roll: %s,"%(self.read_i16(ADDR_TANGAGE), self.read_i16(ADDR_ROULIS)))
		#logging.debug("pitch: %s, roll: %s, temps: %s, sound_speed: %s, ca0: %s, ca1: %s"%(self.read_i16(ADDR_TANGAGE), self.read_i16(ADDR_ROULIS), self.read_i16(ADDR_TEMP_MOY), self.read_i16(ADDR_SOUND_SPEED), self.read_i16(ADDR_GAIN_CA0), self.read_i16(ADDR_GAIN_CA1)))
		data_list = self.read_buf_i16(ADDR_PROFILE_HEADER, SIZE_PROFILE_HEADER + _n_vol*4) 

		logging.debug("processing+transfert delay = %fs"%(datetime.utcnow()-self.timestamp_profile).total_seconds())

		# on passe en litte endian (les données initiales sont en big endian)
		# traitement < 1ms pour 50 cellules sur macbook pro
		data_packed = struct.pack('<%sh'%int(len(data_list)/2), \
			*struct.unpack('>%sh'%int(len(data_list)/2), data_list))
		logging.debug("pack string = '%s'"%'>%sh'%int(len(data_list)/2))

		logging.debug("processing+transfert+swap delay = %fs"%(datetime.utcnow()-self.timestamp_profile).total_seconds())

		return encode_timestamp(self.timestamp_profile) + data_packed
