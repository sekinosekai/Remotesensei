import cv2 
import requests 
import recognition as rec
import redis 
import time
import sys
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

com_ip = "127.0.0.1"
com_port = "6379" # socket port
channel = "Pepper"
save_path = r"C:\Users\38407\Desktop\Analyze"

r = redis.StrictRedis(host=com_ip)
print ("pub start------------------")

faceList = []
cap = cv2.VideoCapture(cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280);
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720);
for i in range(60):
	ret, frame = cap.read() # In case that the first captrued is black
# load face id
img_path = save_path + r"\faces.jpg"
cv2.imwrite(img_path, frame)
img_data = open(img_path, "rb").read()
faceList = rec.facelist_creator(img_data)
cap.release() # release the capture
cv2.destroyAllWindows()

cap = cv2.VideoCapture(cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280);
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720);
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1280,720))
if cap.isOpened():
	n = 0 # analysis starts from number 0
	interval = 3 # the period of time
	t = 1 # repeat time
	global tmp_state
	tmp_state = ""
	# graph
	timeline = np.zeros(5)
	graphState = np.zeros(shape=(4,5))
	ind = np.arange(5)
	plt.figure(figsize=(8,5))
	mngr = plt.get_current_fig_manager()
	mngr.window.wm_geometry("+0+0")
	plt.ion()
	while True:
		ret, frame = cap.read()
		frameTime = time.strftime('%H:%M:%S',time.localtime(time.time())) # time stamp
		print ("TIME ", end="")
		print (frameTime)
		cv2.imshow("contion capture", frame) # display the image
		out.write(frame)
		cv2.moveWindow("contion capture", 625, 0)
		if cv2.waitKey(1) & 0xFF == ord('q'): # type q to stop
			break
		
		img_path = save_path + r"\{}.jpg".format(str(n))
		cv2.imwrite(img_path, frame)
		img_data = open(img_path, "rb").read() # binary
		stateList = rec.state_creator(img_data, faceList, frameTime)
		if stateList: # have value
			# graph
			plt.cla() # clear graph
			plt.clf()
			confList = np.append(graphState[0][1:], stateList.count(0))
			intList = np.append(graphState[1][1:], stateList.count(1))
			disList = np.append(graphState[2][1:], stateList.count(2))
			norList = np.append(graphState[3][1:], stateList.count(3))
			timeline = np.append(timeline[1:], frameTime)
			graphState = np.append([confList, intList, disList], [norList], axis=0)
			width = 0.35
			graphConf = plt.bar(ind, confList, width, color='yellowgreen')
			graphInt = plt.bar(ind, intList, width, bottom=np.array(confList), color='orangered')
			graphDis = plt.bar(ind, disList, width, bottom=(np.array(confList)+intList), color='steelblue')
			graphNor = plt.bar(ind, norList, width, bottom=((np.array(confList)+intList)+disList), color='dimgrey')
			plt.xlabel('time')
			plt.ylabel('number of people')
			plt.xticks(ind, timeline)
			plt.yticks(np.arange(0,5,step=1))
			plt.legend((graphConf[0], graphInt[0], graphDis[0], graphNor[0]), ('Confused', 'Interested', 'Distracted', 'Normal'))
			plt.tight_layout()
			plt.pause(0.05)

			state = Counter(stateList).most_common(1)[0][0]
			print("this time state: " + str(state))
			print("last state: " + str(tmp_state))
			# print (state)
			if state == tmp_state:
				t = t + 1
				print ("repeat"+str(t))
				if t % interval == 0:
					print ("repeat ------------- ", end="")
					print (t)
					if state == 3:
						print ("***normal-----keep going")
					elif state == 2:
						print ("!!!negative-----take actions")
						r.publish(channel, "2") # distracted
					elif state == 1:
						print ("***interested-----keep going")
						r.publish(channel, "1") # interested
					else:
						print ("!!!confused-----take actions")
						r.publish(channel, "0") # confused
			else:
				t = 1
				print("reset t value")
			tmp_state = state # update state

cap.release()
out.release()
cv2.destroyAllWindows()










