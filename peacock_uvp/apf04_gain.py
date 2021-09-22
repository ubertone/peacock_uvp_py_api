#!/usr/bin/env python
# -*- coding: UTF_8 -*-

# @copyright  this code is the property of Ubertone.
# You may use this code for your personal, informational, non-commercial purpose.
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer, Alexandre Schaeffer, Marie Burckbuchler

from math import pow

APF04_RECEPTION_CHAIN_CONSTANT_GAIN = 11.72 # new 14.5  # dB (component after DAC+LNA)
APF04_GAIN_CODE_RATIO = 4.029E-2  # in the chain AD5621 (DAC) + AD8331 (LNA - low noise amplifier), where DAC (12bits-->4096, 3.3V) and gain LNA (50dB/V).

APF04_CODE_MAX_APPLIED = 1241
APF04_CODE_MAX_USER = 4095
APF04_CODE_MIN_USER = -4096
APF04_CODE_MIN_APPLIED = 50


## @brief Conversion of gain slope a1 (in dB) to code ca1. 4 bits shift for precision reasons.
# @param _gain_dB gain slope in dB/m (float)
# @param _r_dvol inter-volume size in m (float)
# @return code (int)
def convert_dB_m2code(_gain_dB, _r_dvol):
	code = int(round((16. * _gain_dB * _r_dvol) / APF04_GAIN_CODE_RATIO, 1))
	code = _truncate(code, APF04_CODE_MAX_USER, APF04_CODE_MIN_USER)
	return code


## @brief Conversion of code ca1 to gain slope a1 (in dB). 4 bits shift for precision reasons.
# @param code (int)
# @param _r_dvol inter-volume size in m (float)
# @return _gain_dB gain slope in dB/m (float)
def convert_code2dB_m(_code, _r_dvol):
	gain_dB = (APF04_GAIN_CODE_RATIO / (16. * _r_dvol)) * _code
	return gain_dB


## @brief Conversion of gain (in dB) to code
# @param _gain_dB gain intercept asked (in dB) (float)
# @return code de gain à appliquer (int)
def convert_dB2code(_gain_dB):
	code = int(round((_gain_dB - APF04_RECEPTION_CHAIN_CONSTANT_GAIN) / APF04_GAIN_CODE_RATIO, 1))
	code = _truncate(code, APF04_CODE_MAX_APPLIED, APF04_CODE_MIN_USER)
	return code


## @brief Conversion of code to gain intercept (in dB)
# @param _code (int)
# @return gain intercept in dB (float)
def convert_code2dB(_code):
	gain_dB = (_code * APF04_GAIN_CODE_RATIO) + APF04_RECEPTION_CHAIN_CONSTANT_GAIN
	return gain_dB


## @brief Conversion of code applied by APF04 in one volume to gain (in dB)
# @param _code (int)
# @return gain applied in a volume in dB (float)
def _convert_code2gain(_code):
	_code = _truncate(_code, APF04_CODE_MAX_APPLIED, APF04_CODE_MIN_APPLIED)
	gain_dB = (_code * APF04_GAIN_CODE_RATIO) + APF04_RECEPTION_CHAIN_CONSTANT_GAIN
	return gain_dB


## @brief Calculation of the table of the gains in dB to apply to each volume of the profile
# @param n_vol number of volumes in the profile
# @param gain_ca0 gain intercept as code (int)
# @param gain_ca1 gain slope as code (int)
# @param gain_max_ca0 blind zone gain limit intercept as code (int)
# @param gain_max_ca1 blind zone gain limit slope as code (int)
# @return Tab_gain table of the gains in dB to apply to each volume of the profile
def calc_gain(n_vol, gain_ca0, gain_ca1, gain_max_ca0, gain_max_ca1):
	# calcul du gain appliquer pour recalcul de l'amplitude des signaux d'entrées
	Tab_gain = []
	i = 0
	while i <= (n_vol - 1):
		G = _convert_code2gain(gain_ca0 + (i * gain_ca1) / 16.)
		G_max = _convert_code2gain(gain_max_ca0 + (i * gain_max_ca1) / 16.)
		if ((G) >= (G_max)):
			Tab_gain.append(pow(10, ((G_max) / 20.)))
		else:
			Tab_gain.append(pow(10, ((G) / 20.)))
		i = i + 1
	return Tab_gain


## @brief troncate value with min/max limit
# @param value : value to troncate
# @param limit_max : max limit
# @param limit_min : min limit
def _truncate(value, limit_max, limit_min):
	return max(min(value, limit_max), limit_min)

# TODO revoir cette fonction test
# pour le test uniquement, lancer python ./apf_gain.py
# if __name__ == "__main__":

	# ~ print "for 45db (LO): use %d"%convert_dB2code ( 45 )
	# ~ print "for 68db (LO): use %d"%convert_dB2code ( 68 )
	# ~ print "for 80db (HI): use %d"%convert_dB2code ( 85 )

	# for i in range(0, 100, 1):
	# 	adb = convert_code2dB(ca_code)
	# 	print "for a0=%f db : use %d  an it return hilo %d and ca0 %f" % (i, ca_code, hilo, adb)
	#
	# # ~ for j in range(5,10) :
	# for i in range(0, 300, 10):
	# 	ca_code = convert_dB_m2code(i, 5.92 * 1e-3)
	# 	adb = convert_code2dB_m(ca_code, 5.92 * 1e-3)
	# 	print "for a1=%f db and r_vol = %f mm : use %d  an it return ca1 %f" % (i, 5.92, ca_code, adb)
