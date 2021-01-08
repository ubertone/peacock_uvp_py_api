#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @copyright  this code is the property of Ubertone. 
# You may use this code for your personal, informational, non-commercial purpose. 
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer, Marie Burckbuchler

import struct # Struct est utilisée pour extraite les données séries  
import serial # Utilisé pour récuperer les donnée vennant de la liaison Série RS485
from sys import platform
import traceback
import logging

from .ap_exception import ap_hardware_error
from .modbus_crc import crc16

# TODO 1 : mettre à jour, créer un apf04_exception ?
#ap_hardware_error(3100, "No APF04 found.")
#ap_hardware_error(3101, "Warning, undefined OS for USB port")
#ap_hardware_error(3102, "Read_buf_i16 : read fail\n")
#ap_hardware_error(3103, "Write_i16 : write FAIL\n")
#ap_hardware_error(3104, "Write : FAIL\n")

# TODO voir qui récupère les exception de hardware qui ne répond pas : à priori apf04_handler

def hex_print (_bytes):
	""" @brief print a byte array in hexadecimal string
	"""
	print (''.join('%02x'%i for i in _bytes))

class Apf04Modbus ():
	"""
	@brief Gestion de la communication Modbus avec l'APF04
	@param _baudrate : vitesse de communication, 57600 bits par seconde par defaut

	_baudrate peut avoir pour valeur 230400 115200 57600 ...

	modbus est en big-endian (défaut)
	l'adressage est fait en 16 bits.
	"""
	def __init__(self, _baudrate=230400, _dev=None):
		"""
		@brief Initialisation de la couche communication de l'instrument
		"""
		# Default device address on modbus
		self.apf04_addr = 0x04

		# TODO mettre dans apf04_addr_cmd.py
		self.addr_ram_begin =  0x0000
		self.addr_ram_end =    0x07FF
		self.addr_reg_action = 0xFFFD

		logging.debug("Platform is %s", platform)

		# TODO try / except serial.serialutil.SerialException : raise ap_hardware_error(...
		if _dev :
			self.usb_device = _dev
		else :
			# In case of a Linux system, we can find the port of the APF04 automatically thanks to the serial.tools.list_ports library and knowing that the RS485 to USB adapter has PID:VID = 0403:6001
			# TODO: Mettre un try catch autour des tests if. Si usb_device n'est pas défini après, on quitte le process.
			if platform == "linux" or platform == "linux2" or platform == "darwin": # linux and Mac OS
				import serial.tools.list_ports as lPort
				found = False
				reslt = lPort.comports()
				for res in reslt:
					if "0403:6001" in res[2]: # dongle USB avec alim
						logging.debug("This is APF04 Device: %s", res[2])
						found = True
						self.usb_device = res[0]
					elif "1A86:7523" in res[2]: # dongle USB sans alim
						logging.debug("This is APF04 Device: %s", res[2])
						found = True
						self.usb_device = res[0]
				if found == False: # no device were found on USB
					logging.info("No APF04 found on USB port. Setting /dev/ttyAMA0 as default.")
					self.usb_device = '/dev/ttyAMA0' # this is the default device on ubertux2/batpacker
					#raise ap_hardware_error(3100, "No APF04 found on USB port.")

			elif platform == "cygwin": # cygwin
				#self.usb_device = "/dev/ttyS3" # WARNING not tested yet with pymodbus, should be modified manually
				logging.info("Software not configured for Cygwin yet")
				ap_hardware_error(3101, "Warning, undefined OS for USB port")

			elif platform == "win32": # Windows
				self.usb_device = "COM10" # WARNING not tested yet with pymodbus, should be modified manually
			else :
				raise ap_hardware_error(3101, "Warning, undefined OS for USB port")

		logging.debug("usb_device is at %s with baudrate %s"%(self.usb_device, _baudrate))

		self.ser = serial.Serial(self.usb_device, _baudrate, timeout=2., \
				bytesize=8, parity='N', stopbits=1, xonxoff=0, rtscts=0)

		# In order to reduce serial lattency of the linux driver, you may set the ASYNC_LOW_LATENCY flag :
		# setserial /dev/<tty_name> low_latency

		#la lecture et l'écriture de bloc sont segmentées en blocs de 123 mots 
		# Modbus limite les blocs à un maximum de 123 mots en ecriture et 125 mots en lecture
		self.max_seg_size=123

		logging.debug("end init")

	def __del__(self):
		# close serial port
		try : # au cas où le constructeur a planté
			self.ser.close()
		except :
			pass

	def set_timeout(self, _timeout):
		try :
			logging.debug ("timeout is %s , set to %s"%(self.ser.timeout , _timeout))
			# timeout pour la lecture des données :
			self.ser.timeout = _timeout
			logging.debug ("now timeout is %s"%(self.ser.timeout))
		except serial.serialutil.SerialException:
			self.log("hardware apparently disconnected")
			#raise ap_hardware_error(3107, "FAIL to set timeout on modbus")

	
	# @ verification de l'existance de la zone memoire
	# @param _begin : addresse de début en octets
	# @param _size : taille du bloc en mots (16 bits)
	def __check_addr_range(self, _begin, _size):
		# adresses des blocs mémoire :
		assert(_begin>=self.addr_ram_begin)
		if _begin>self.addr_ram_end:
			assert _begin!=self.addr_reg_action and _size!=1, "Warning, access at %d, size= %d bytes not allowed"%(_begin, _size)

	def __read__(self, _size):
		if _size == 0:
			raise ap_protocol_error(23442, "ask to read null size data" )

		try :
			read_data = self.ser.read(_size)
		except serial.serialutil.SerialException:
			self.log("hardware apparently disconnected")
			read_data = b''
			#raise ap_hardware_error( ...

		if len (read_data) != _size :
			if len (read_data) == 0:
				logging.debug ("WARNING timeout, no answer from device")
				raise ap_hardware_error(23443, "timeout : device do not answer (please check cable connexion or baudrate)" )
			else :
				logging.debug ("WARNING timeout, uncomplete answer from device (%d/%d)"%(len (read_data), _size))
				raise ap_hardware_error(23444, "timeout : uncomplete answer from device (please check timeout or baudrate) (%d/%d)"%(len (read_data), _size))
		
		return read_data


	############## Read functions ###############################################
	
	# @brief fonction de lecture d'un mot de 16 bits signé
	# @param _addr : adresse (en octet) du mot
	# @return : entier signé
	# les données sont transmises en big endian (octet de poids faible en premier)
	def read_i16 (self, _addr):
		return struct.unpack(">h",self.read_seg_16(_addr , 1))[0]

	def read_list_i16(self, _addr, _size):
		return struct.unpack(">%dh"%_size,self.read_seg_16(_addr , _size))


	# @brief fonction de lecture de mots de 16 bits signés ou non-signé en RAM
	# @param _addr : adresse (en octet) du premier mot à lire
	# @param _size : taille en nombre de mots du bloc à lire
	# les données sont transmises en big endian (octet de poids fort en premier)
	def read_seg_16(self, _addr, _size):
		assert (_size <= self.max_seg_size)  # segment de 125 mots (max en lecture)
		try:
			logging.debug ("reading %d words at %d"%(_size, _addr))
			# on utilise la fonction modbus 3 pour la lecture des octets
			#self.__check_addr_range(_addr, 2 * _size)

			# request read 
			read_query = struct.pack(">BBHh",self.apf04_addr, 0x03, _addr, _size )
			read_query += struct.pack(">H",crc16 (read_query) )
			#print ("read query = ")
			#hex_print(read_query)
			try :
				self.ser.write(read_query)
			except serial.serialutil.SerialException:
				self.log("hardware apparently disconnected")
				#raise ap_hardware_error( ...

			# read answer
			slave_response = self.__read__(3)

			if slave_response[1] != 3:
				logging.info ("WARNING error while reading %s"%slave_response)

			slave_response += self.__read__(slave_response[2]+2)

			#print ("slave answer = ")
			#hex_print(slave_response)

			# check crc
			#print ("%X"%crc16 (slave_response[0:-2]))
			#print ("%X"%struct.unpack(">H",slave_response[-2:]))
			assert (crc16 (slave_response[0:-2]) == struct.unpack(">H",slave_response[-2:])[0])

		except:
			# TODO traiter les différentes erreurs, se mettre en 3 MBaud sur pi0W (bcp de buffer overflow !)
			logging.info ("Read_buf_i16 : read fail\n")
			raise # TODO define exception

		return slave_response[3:-2]


	# @brief fonction de lecture de mots de 16 bits signés en RAM
	# @param _addr : adresse (en octet) du premier mot à lire
	# @param _size : taille en nombre de mots du bloc à lire
	# @return : liste des mots
	# les données sont transmises en big endian (octet de poids faible en premier)
	def read_buf_i16 (self, _addr , _size):
		data = b''
		addr = _addr
		remind = _size
		logging.debug ("reading %d words at %d"%(_size, _addr))
		while remind :
			logging.debug ("remind = %s ; self.max_seg_size = %s ; div : %s"%(remind, self.max_seg_size, remind/self.max_seg_size))
			if remind/self.max_seg_size>=1:
				logging.debug ("read max_seg_size")
				seg_size=self.max_seg_size
			else :
				seg_size = remind
				logging.debug ("read remind")
			data+=self.read_seg_16(addr , seg_size)
			addr+=seg_size #  addr en mots de 16 bits
			remind-=seg_size
		#print( "__Read_buf : %d readed"%(int(addr - _addr)) )
		return data



	############## Write functions ##############################################


	# @brief fonction d'écriture d'un mot 16 bit signé
	# @param _value : valeur du mot à écrire
	# @param _addr: adresse de destination du mot
	def write_i16 (self, _value, _addr):
		try:
			self.write_buf_i16 ([_value], _addr)
		except :
			print(traceback.format_exc())
			raise ap_hardware_error(3103, "Write_i16 : FAIL to write 0%04x at %d\n"%(_value, _addr))

	# @brief fonction d'écriture de mots de 16 bits signés (dans la RAM ou dans les registres)
	# @param _data : données en liste (taille max de 123 mots)
	# @param _addr : adresse (en octet) du premier mot à écrire
	# 
	# les données sont transmises en big endian (octet de poids faible en premier)
	# ici on ne gère pas de boucle sur un "write_seg_16" car on n'a pas besoin d'écrire de gros blocs de données
	def write_buf_i16 (self, _data, _addr):
		# segmenter en blocs de 123 mots (max en ecriture)
		assert (len(_data)<=self.max_seg_size)
		try:
			# request read 
			write_query = struct.pack(">BBHhB%sh"%len(_data),self.apf04_addr, 16, _addr, len(_data), 2*len(_data), *_data )
			write_query += struct.pack(">H",crc16 (write_query) )

			try:
				#print (write_query)
				self.ser.write(write_query)
			except serial.serialutil.SerialException:
				self.log("hardware apparently disconnected")
				#raise ap_hardware_error( ...

			# read answer
			slave_response = self.__read__(2)
			# TODO 1 : format de la trame d'erreur et codes d'erreurs effectivement traités
			if slave_response[1] == 16 :
				slave_response += self.__read__(6)
				# TODO sur le principe il faudrait vérifier que le bon nombre de mots a été écrit
			else:
				# TODO traiter les erreurs selon doc 
				size = struct.unpack("B",self.__read__(1))[0]
				print ("size following : %d"%size)
				self.__read__(size)
				print("error while writting")
				print (slave_response)

		except :
			print(traceback.format_exc())
			raise #ap_hardware_error(3104, "Write : FAIL\n")
