#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer

from datetime import datetime, timezone
from time import mktime
from struct import pack

# temps ZERO (Ubertone Epoch)
UBT_EPOCH = datetime(2020, 1, 1, tzinfo=timezone.utc)

def convert_timestamp(_datetime):
	""" 
	ubertone's epoch :
	- 01/01/2020 starting from version 2.01
	"""
	
	timestamp = mktime(_datetime.timetuple()) + _datetime.microsecond/1e6 - mktime(UBT_EPOCH.timetuple())
	#       timestamp (epoch)    2*int16  Epoch en secondes MSB + LSB (*)
	#       timestamp extension  int16    En millisecondes
	#print ("convert_timestamp : %s -> %f"%(_datetime, timestamp))

	# DIRECTIVE WARNING : attention à ne pas mélanger int16 et int32. En effet la machine est susceptible d'aligner les données sur 32 bits.
	#   du coup un pack "hih" vas donner le premier short (16 bits) suivi par 0x0000 puis le second entier (int32) !!!
	# TODO forcer l'endianness ?
	return pack("hhh", int((int(timestamp)>>15)&0x0000FFFF), int(int(timestamp)&0x00007FFF),\
										  int(1000.*(timestamp%1)))

def convert_packed_timestamp(pF, pf, ms):
	ms = float(ms)/1000.
	pF2 = int(pF)<<15
	sec = int(pF2|pf)
	timestamp = sec+ms
	relative_timestamp = datetime.fromtimestamp(timestamp)

	absolute_timestamp = UBT_EPOCH+relative_timestamp
	return absolute_timestamp
