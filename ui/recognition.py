import cv2
import json
import requests
import matplotlib.pyplot as plt 
import csv
import numpy as np
from datetime import datetime
import os
import classifierKNN as knn
import time

subscription_key = "e5b6687756d44e07ba4344fc00f5e50a"
threshold = 1.38
stateMap = {"0": "confused", "1": "interested", "2": "distracted", "3": "normal"}

def classifier_setup():
	knn.train()

def state_creator(facedata):
	detect_url = "https://southeastasia.api.cognitive.microsoft.com/face/v1.0/detect"
	detect_headers = {'Ocp-Apim-Subscription-Key': subscription_key, "Content-Type": "application/octet-stream"}
	detect_params = {
		'returnFaceId': 'true',
		'returnFaceLandmarks': 'true',
		'returnFaceAttributes': 'emotion',
		'recognitionModel': 'recognition_02'
	}
	stateList = []
	stateName = []
	locList = []
	faceList = []
	face_num = 0
	tmp_left = 0
	qs = lambda xs : ( (len(xs) <= 1 and [xs]) or [ qs( [x for x in xs[1:] if x['faceRectangle']['left'] >= xs[0]['faceRectangle']['left']] ) + [xs[0]] + qs( [x for x in xs[1:] if x['faceRectangle']['left'] < xs[0]['faceRectangle']['left']] ) ] )[0]
	
	response = requests.post(detect_url, params=detect_params, headers=detect_headers, data=facedata)
	response.raise_for_status()
	faces = response.json()
	for i in faces:
		faceList.append(i)
		face_num += 1
	faceList = qs(faceList)
	if faceList:
		for i in faceList: #取的字典
			landmark = i['faceLandmarks']
			pupilLeft = landmark['pupilLeft']
			pupilRight = landmark['pupilRight']
			eyeLeftOuter = landmark['eyeLeftOuter']
			eyeLeftInner = landmark['eyeLeftInner']
			eyeRightInner = landmark['eyeRightInner']
			eyeRightOuter = landmark['eyeRightOuter']
			emotionDict = i['faceAttributes']['emotion']
			emotionList = []
			for j in emotionDict.values(): # emotion list
				emotionList.append(j)
			# print(emotionList)
			inputX = np.array(emotionList,ndmin=2)
			# print(inputX)
			prediction = knn.classify(inputX) # classification
			state = prediction.tolist()[0]

			if state in (2,3):
				calcD = lambda x1,y1,x2,y2: ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
				calcCOSB = lambda a,b,c: (a ** 2 + c ** 2 - b ** 2) / (2 * c)
				calcCOSA = lambda a,b,c: (b ** 2 + c ** 2 - a ** 2) / (2 * c)
				# calculate the location of pupil
				aLeft = calcD(eyeLeftOuter['x'], eyeLeftOuter['y'], pupilLeft['x'], pupilLeft['y'])
				bLeft = calcD(pupilLeft['x'], pupilLeft['y'], eyeLeftInner['x'], eyeLeftInner['y'])
				cLeft = calcD(eyeLeftOuter['x'], eyeLeftOuter['y'], eyeLeftInner['x'], eyeLeftInner['y'])
				bRight = calcD(pupilRight['x'], pupilRight['y'], eyeRightOuter['x'], eyeRightOuter['y'])
				aRight = calcD(eyeRightInner['x'], eyeRightInner['y'], pupilRight['x'], pupilRight['y'])
				cRight = calcD(eyeRightInner['x'], eyeRightInner['y'], eyeRightOuter['x'], eyeRightOuter['y'])
				offsetLeft = calcCOSB(aLeft, bLeft, cLeft) / calcCOSA(aLeft, bLeft, cLeft)
				offsetRight = calcCOSB(aRight, bRight, cRight) / calcCOSA(aRight, bRight, cRight)
				# print([offsetLeft,offsetRight])
				if max([offsetLeft, offsetRight]) > threshold or min ([offsetLeft, offsetRight]) < (1/threshold) :
					state = 2 #set to distracted
				else:
					state = 3 # set to normal
			stateList.append(state)
			stateName.append(stateMap[str(state)])
		print ("stateList ", end="")
		print (stateName)
		return stateList, face_num
	else:
		return [], 0

#--------------------------TESTING
if __name__ == '__main__':
	faceList = []
	classifier_setup()
	cap = cv2.VideoCapture(cv2.CAP_DSHOW)
	for i in range(30):
		ret, frame = cap.read() # In case that the first captrued is black
	if cap.isOpened():
		n = 0 # analysis starts from number 0
		interval = 3 # the period of time
		tmp_state = ""
		t = 1
		while True:
			ret, frame = cap.read()
			frameTime = time.strftime('%H:%M:%S',time.localtime(time.time())) # time stamp
			print (frameTime)
			cv2.imshow("capture", frame) # display the image
			if cv2.waitKey(1) & 0xFF == ord('q'): # type q to stop
				break
			save_path = r"C:\Users\38407\Desktop\Analyze"
			
			img_path = save_path + r"\{}.jpg".format(str(n))
			cv2.imwrite(img_path, frame)
			img_data = open(img_path, "rb").read() # binary
			state = state_creator(img_data)
			if state == tmp_state:
				t = t + 1
				if t % interval == 0:
					if state == 3:
						print ("normal-----keep going")
					elif state == 2:
						print ("negative-----take actions")
					elif state == 1:
						print ("interested-----keep going")
					elif state == 0:
						print ("confused-----take actiosn")
					else:
						print ("NONE")
			else:
				t = 0
			tmp_state = state # update state
			n +=1







