#!/usr/bin/env python
# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone. 
# You may use this code for your personal, informational, non-commercial purpose. 
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer
# ap_hardware_error
#		40 "Unable to connect to the device" : impossible de se connecter au driver
#		41 "lost connection with the driver, reconnecting" : 

#raise ap_protocol_error (100, "WARNING a bloc has been requested")
#raise ap_protocol_error (101, "already one bloc requested, should stop manually")
#raise ap_protocol_error(104, "WARNING running another config, no inst available")
#raise ap_protocol_error (102, "no config available")
#raise ap_protocol_error (103, "config %d/%d not available")
#raise ap_protocol_error (110, "inst/mov profile not available")

#raise ap_protocol_error (120, "empty chunk")
#raise ap_protocol_error (122, "unexpected chunk content")
#raise ap_protocol_error (126, "socket timeout")
#raise ap_protocol_error (128, "bloc has been interupted")

## \brief Classe ap_base_exception (Exception) qui gère les exceptions spéciales.
class ap_base_exception (Exception):
	def __init__(self, _code, _message):
		self.code = _code
		self.message = _message

	def __str__(self):
		return "base_exception %d : %s"%(self.code, self.message)

## \brief Classe ap_release_exception qui gère les exceptions lié à la libération d'un évenement
# ex. une fonction attends un évenement qui est annulé
class ap_release_exception (ap_base_exception):
	def __str__(self):
		return "release_exception %d : %s"%(self.code, self.message)

## \brief Classe ap_hardware_error qui gère les erreurs liés au hardware
# ex. driver qui ne répond pas, ressource non disponible...
class ap_hardware_error (ap_base_exception):
	def __str__(self):
		return "hardware_error %d : %s"%(self.code, self.message)

## \brief Classe ap_protocol_error qui gère les erreurs de protocole
# ex. on demande a modifier les settings alors qu'un bloc est en cours pour une requete d'enregistrement...
class ap_protocol_error (ap_base_exception):
	def __str__(self):
		return "ap_protocol_error %d : %s"%(self.code, self.message)

