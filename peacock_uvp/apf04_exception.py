#!/usr/bin/env python
# -*- coding: UTF_8 -*-
# @copyright  this code is the property of Ubertone. 
# You may use this code for your personal, informational, non-commercial purpose. 
# You may not distribute, transmit, display, reproduce, publish, license, create derivative works from, transfer or sell any information, software, products or services based on this code.
# @author Stéphane Fischer

class apf04_exception (Exception):
	""" @brief class for APF04 specific exceptions """
	def __init__(self, _code, _message):
		self.code = _code
		self.message = _message

	def __str__(self):
		return "apf04_exception %d : %s"%(self.code, self.message)
