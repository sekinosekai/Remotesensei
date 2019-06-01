# -*- coding:utf-8 -*-
import redis
import time
import random
import control as co
from naoqi import ALProxy
import threading
import re

com_ip = "127.0.0.1"
com_port = "6379"
robot_ip = co.ROBOT_IP
robot_port = co.ROBOT_PORT
channel = "Pepper"
state = "default"
gestnum = 15
counter = 1
# init vo100, sp80, pa100
VOLUME = 70 #100
SPEED = 90 # jp 110
PAUSE = 0
LANG = "en"
def action():
	r = redis.StrictRedis(host=com_ip)
	ps = r.pubsub()
	ps.subscribe(channel)
	tmp_data = ""
	state = "default"
	print ("sub start----------------------")
	_init()
	for msg in ps.listen():
		if msg["type"] == "message":
			data = msg["data"]
			if data == tmp_data:
				counter = counter + 1
			else:
				counter = 1 # reset counter
			if data == "2":
				# do behaviour
				if counter == 1:
					state = "d1"
				elif counter == 2:
					state = "d2"
				else:
					state = "d3"
			elif data == "0":
				# change velocity
				if counter == 1:
					state = "t1"
				elif counter == 2:
					state = "t2"
				else:
					state = "t3"
			else:
				state = "default"
			tmp_data = data
			action_dict[state]()

def speech():
	global _global_dict
	co.motion("reset")
	tts = ALProxy("ALTextToSpeech", robot_ip, robot_port)
	# print (tts.getAvailableVoices())
	if LANG == "jp":
		tts.setLanguage("Japanese")
		# tts.setVoice("naoenu")
		filePath = r".\scriptEB3.txt"
		divider = r" "
	elif LANG == "en": 
		tts.setLanguage("English")
		# filePath = r".\scriptEBen1.txt"
		filePath = r".\enscript.txt"
		divider = r"\.|\?|,|:"
	with open(filePath, "r") as script:
		lines = script.read()
		for line in re.split(divider, lines):
			try:
				print (line)
				print("---------------------------")
				print(state)
				tts.post.say("\\vol={}\\\\rspd={}\\\\pau={}\\".format(_global_dict["VOLUME"], _global_dict["SPEED"], _global_dict["PAUSE"]) + line)
				time.sleep(3)
			except:
				pass
def _init():
	global _global_dict
	_global_dict = {"VOLUME": VOLUME, "SPEED": SPEED, "PAUSE": PAUSE}
	stick = ALProxy("ALAutonomousLife", robot_ip, robot_port)
	stick.setAutonomousAbilityEnabled("All", False)

def set_speech(key,value):
	global _global_dict
	_global_dict[key] = value

def reset():
	print ("keep going-------------")
	global _global_dict
	_global_dict = {"VOLUME": VOLUME, "SPEED": SPEED, "PAUSE": PAUSE}
	leds = ALProxy("ALLeds", robot_ip, robot_port)
	leds.fadeRGB( "FaceLeds", "white", 0.1)
	co.motion("reset")

def d1():
	print ("distracted ------------")
	gest = "b" + str(random.randint(1, gestnum))
	co.motion(gest)

def d2():
	print ("distracted *3------------")
	co.leds()

def d3():
	print ("distracted *2------------")	
	set_speech("VOLUME", 150)

def t1():
	print ("confused ------------")
	gest = "b" + str(random.randint(1, gestnum))
	co.motion(gest)

def t2():
	print ("confused *2------------")
	set_speech("SPEED", 40)

def t3():
	print ("confused *3------------")
	set_speech("PAUSE", 900)

action_dict = {"d1": d1, "d2": d2, "d3": d3, "t1": t1, "t2": t2, "t3": t3, "default": reset}

at = threading.Thread(target=action)
at.start()
sp = threading.Thread(target=speech)
sp.start()
