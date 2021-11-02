#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @copyright  this code is the property of Ubertone. 
# You may use this code for your personal, informational, non-commercial purpose. 
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer

import os
import json
import logging
logging.basicConfig(level=logging.DEBUG)

## Adresses et commandes de l'APF04

# numéro de commande d'inaction (tourne en boucle en attendant une commande) 
CMD_NULL = 0 
# numéro de commande pour l'arrêt de l'action en cours 
CMD_STOP = 1 
# numéro de commande mode bloquant 
CMD_PROFILE_BLOCKING = 3 
# numéro de commande mode non bloquant 
CMD_PROFILE_NON_BLOCKING = 4 
# numéro de commande mesure avec remontée des IQ 
CMD_PROFILE_IQ = 6 
# numéro de commande démarrage du mode auto 
CMD_START_AUTO = 2 
# numéro de commande verification de la configuration courante 
CMD_CHECK_CONFIG = 5 
# numéro de commande de réinitialisation du settings
CMD_INIT_SETTINGS = 7
# mesure de niveau 
CMD_MEAS_LEVEL = 20 
# numéro de commande pour un test de LED 
CMD_TEST_LED = 190 
# numéro de commande pour une mesure de température + pitch + roll 
CMD_TEST_I2C = 195 

# ces 5 adresses sont considérées comme fixes et qui ne changeront jamais.
ADDR_ACTION = 0xFFFD

ADDR_VERSION_C    = 0x0000 # nécessaire pour pouvoir justement déterminer le dict des autres adresses
ADDR_VERSION_VHDL = 0xFFFE
ADDR_MODEL_YEAR   = 0x0001
ADDR_SERIAL_NUM   = 0x0002

def get_addr_dict(version_c, addr_json=None):
    """
    Gets the addresses in RAM given the firmware version.

    Args:
        version_c: two digits number version
        addr_json: possible to give directly a json file

    Returns:
        Dictionnary with the addresses names as keys and addresses in hexa as values.
    """

    if addr_json:
        with open(addr_json) as json_file:
	        addr_dict = json.loads(json_file.read())
    else:
        if version_c <= 52 and version_c >= 47:
            addr_json = os.path.abspath(__file__).split('/peacock_uvp_py_api')[0] + "/peacock_uvp_py_api/peacock_uvp/addr_S-Firmware-47.json"
        else:
            addr_json = os.path.abspath(__file__).split('/peacock_uvp_py_api')[0] + "/peacock_uvp_py_api/peacock_uvp/addr_S-Firmware-"+str(version_c)+".json"
        if addr_json.split("/")[-1] in os.listdir(os.path.abspath(__file__).split('/peacock_uvp_py_api')[0] + "/peacock_uvp_py_api/peacock_uvp/"):
            with open(addr_json) as json_file:
                addr_dict = json.loads(json_file.read())
        else:
            # TODO mb 20/10/2021 choisir si on veut mettre un comportement par défaut ou fonctionner par exception
            logging.debug("WARNING: Unknown Addresses for this S-Firmware version.")
            addr_dict = None
    
    logging.debug(os.listdir("."))
    logging.debug("addr json: ", addr_json)
    logging.debug("addr dict: ", addr_dict)

    # conversion of haxa strings to hexa number
    if addr_dict:
        for key,value in addr_dict.items():
            if isinstance(value, str):
                if "x" in value:
                    addr_dict |= {key:int(value, 16)}

    logging.debug("addr dict converted: ", addr_dict)

    return addr_dict

# ===============================================
# DESCRIPTION OF AVAILABLE ADDRESSES IN THE DICT:
# ===============================================
#ADDR_SOUND_SPEED_AUTO
#ADDR_SOUND_SPEED_SET

#Adresse contenant l'adresse de la configuration de séquencement ultrasons demandée par Modbus. Elle est suivie par les 3 config partagées avec Modbus.
#ADDR_CONFIG_ID
#Adresse de départ de la zone contenant les config
#ADDR_CONFIG
#Décallage entre chaque config
#OFFSET_CONFIG
#SIZE_CONFIG

# ----- Mesures Sensors -----
#Adresse du tanguage moyen mesuré (à destination du Modbus)
#ADDR_TANGAGE
#Adresse du roulis moyen mesuré (à destination du Modbus)
#ADDR_ROULIS
#Adresse de la température moyenne mesurée (à destination du Modbus)
#ADDR_TEMP_MOY

# ---- En-tête des profils ----
#ADDR_SOUND_SPEED
#ADDR_GAIN_CA0
#ADDR_GAIN_CA1

#Adresse des profils de vitesse et amplitude
#ADDR_PROFILE_HEADER # adresse du tangage, 1er sensor
#SIZE_PROFILE_HEADER
#ADDR_PROFILE_DATA # le début des données
