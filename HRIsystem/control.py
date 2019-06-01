# !/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import time
import random
import numpy
import csv
from naoqi import ALProxy
import re

# ROBOT_IP = "165.93.38.108"
ROBOT_IP = "192.168.11.51"
ROBOT_PORT = 9559
motionProxy = ALProxy("ALMotion", ROBOT_IP, ROBOT_PORT)
LANG = "en"
VOLUME = 70
SPEED = 150
PAUSE = 500
def speech():
	global state
	global _global_dict
	motion("reset")
	tts = ALProxy("ALTextToSpeech", ROBOT_IP, ROBOT_PORT)
	if LANG == "jp":
		tts.setLanguage("Japanese")
		filePath = r".\scriptjp.txt"
		divider = r'[\s]'
	elif LANG == "en":
		tts.setLanguage("English")
		filePath = r".\script.txt"
		divider = r"\.|\?|,|:"
	with open(filePath, "r") as script:
		lines = script.read()
		for line in re.split(divider, lines):
			print (line)
			action_dict[state]()
			tts.say("\\vol={}\\\\rspd={}\\\\pau={}\\".format(_global_dict["VOLUME"], _global_dict["SPEED"], _global_dict["PAUSE"]) + line)

def leds():
	leds = ALProxy("ALLeds", ROBOT_IP, ROBOT_PORT)
	rDuration = 0.1
	for i in range(30):
		leds.fadeRGB( "FaceLeds", 0Xff775c, rDuration )
		time.sleep(0.3)
		leds.fadeRGB( "FaceLeds", "white", rDuration )
		time.sleep(0.3)

def StiffnessOn(proxy):
	pNames = "Body"
	pStiffnessLists = 1.0
	pTimeLists = 1.0
	proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def motion(gest):
	filePath = r"C:\Users\38407\Desktop\FINAL\Code\robotcontrol\{}.txt".format(gest)
	StiffnessOn(motionProxy)
	motionProxy.stopMove()
	names = list()
	times = list()
	keys = list()
	with open(filePath, 'r') as fr:
		for command in fr.readlines()[6:]:
			if "try" in command:
				break
			print (command)
			if command != '\n':
				exec(command)
	motionProxy.post.angleInterpolation(names, keys, times, True)
	motionProxy.stopMove() 



if __name__ == '__main__':
	# _init()
	speech()
	# leds()
	# leds = ALProxy("ALLeds", ROBOT_IP, ROBOT_PORT)
	# leds.fadeRGB( "FaceLeds", "white", 0.1)

