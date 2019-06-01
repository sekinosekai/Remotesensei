import cv2
import json
import requests
import matplotlib.pyplot as plt 
import csv
import numpy as np
from datetime import datetime
import os
import classifierKNN as KNN
import time

subscription_key = "e5b6687756d44e07ba4344fc00f5e50a"
threshold = 1.38

#------ no headers 
def csv_creator(row, path): 
	with open(path,'a', newline='') as f:
		f_csv = csv.writer(f)
		f_csv.writerow(row)

def facelist_creator(facedata):
	# face detect api
	detect_url = "https://southeastasia.api.cognitive.microsoft.com/face/v1.0/detect"
	detect_headers = {'Ocp-Apim-Subscription-Key': subscription_key, "Content-Type": "application/octet-stream"}
	detect_params = {
		'returnFaceId': 'true',
		'returnFaceLandmarks': 'true',
		'returnFaceAttributes': 'emotion',
		'recognitionModel': 'recognition_02'
	}
	faceList = [] # faces in a picture
	face_num = 0
	tmp_top = 0
	# load face id
	response = requests.post(detect_url, params=detect_params, headers=detect_headers, data=facedata)
	response.raise_for_status()
	faces = response.json()
	for i in faces: # faces loading...
		faceID = i["faceId"]
		faceTop = i['faceRectangle']['top']
		if faceTop >= tmp_top:
			faceList.insert(0, i["faceId"])
			tmp_top = faceTop
		else:
			faceList.append(faceID)
		face_num += 1 # count number of faces
	print (str(face_num) + " persons") # test-----------------
	return faceList

def state_creator(facedata, facelist, time):
	detect_url = "https://southeastasia.api.cognitive.microsoft.com/face/v1.0/detect"
	detect_headers = {'Ocp-Apim-Subscription-Key': subscription_key, "Content-Type": "application/octet-stream"}
	detect_params = {
		'returnFaceId': 'true',
		'returnFaceLandmarks': 'true',
		'returnFaceAttributes': 'emotion',
		'recognitionModel': 'recognition_02'
	}
	simi_url = "https://southeastasia.api.cognitive.microsoft.com/face/v1.0/findsimilars"
	simi_headers = {'Ocp-Apim-Subscription-Key': subscription_key, "Content-Type": "application/json"}
	csvList = [] # used for csv file
	stateList = []

	data, labels = KNN.createDataset() # KNN dataset
	classifier = KNN.train(data, labels) # training
	response = requests.post(detect_url, params=detect_params, headers=detect_headers, data=facedata)
	response.raise_for_status()
	faces = response.json()
	for i in faces:
		landmark = i['faceLandmarks']
		pupilLeft = landmark['pupilLeft']
		pupilRight = landmark['pupilRight']
		eyeLeftOuter = landmark['eyeLeftOuter']
		eyeLeftInner = landmark['eyeLeftInner']
		eyeRightInner = landmark['eyeRightInner']
		eyeRightOuter = landmark['eyeRightOuter']
		emotionDict = i['faceAttributes']['emotion']
		faceID = i['faceId']
		payload = {"faceId": faceID, "faceIds": facelist}
		response = requests.post(simi_url, headers=simi_headers, data=json.dumps(payload))
		response.raise_for_status()
		simi_list = response.json()
		if simi_list: # find the same face
			simi_ID = simi_list[0]['faceId']
			print()
			print("ID: ", end="")
			print (simi_ID)				
			for candi_ID in facelist:
				if simi_ID == candi_ID: # map the id with the location in the list
					emotionList = []
					emotionList.append(time)
					for j in emotionDict.values():
						emotionList.append(j)
					inputX = np.array(emotionList[1:],ndmin=2)
					prediction = KNN.classify(classifier, inputX)
					state = prediction.tolist()[0]

					if state == 2:
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
						print([offsetLeft,offsetRight])
						if max([offsetLeft, offsetRight]) > threshold or min ([offsetLeft, offsetRight]) < (1/threshold) :
							pass
						else:
							state = 3 # set to normal

					emotionList.append(state)
					file_path = "C:\\Users\\38407\\Desktop\\%s.csv" % facelist.index(candi_ID)
					csv_creator(emotionList, file_path)
					stateList.append(state)
		else:
			print ("face unknow")
			return []
	print ("stateList ", end="")
	print (stateList)
	return stateList


#--------------------------TESTING-------------------------
if __name__ == '__main__':
	faceList = []
	cap = cv2.VideoCapture(cv2.CAP_DSHOW)
	for i in range(30):
		ret, frame = cap.read() # In case that the first captrued is black
	# load face id
	save_path = r"C:\Users\38407\Desktop\Analyze"
	img_path = save_path + r"\faces.jpg"
	cv2.imwrite(img_path, frame)
	img_data = open(img_path, "rb").read()
	faceList = facelist_creator(img_data)
	cap.release() # release the capture
	cv2.destroyAllWindows()

	cap = cv2.VideoCapture(cv2.CAP_DSHOW)
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
			
			img_path = save_path + r"\{}.jpg".format(str(n))
			cv2.imwrite(img_path, frame)
			img_data = open(img_path, "rb").read() # binary
			state = state_creator(img_data, faceList, frameTime)
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







