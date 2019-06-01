# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainw.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

import sys
import time
import cv2
import requests 
import recognition as rec
import threading
import numpy as np
from collections import Counter
from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

stateList = []
frameTime = ""
locList = []
faceList = []
cur_image = np.array([])
stuNum = 0
stopped = True
class RecordVideo(QtCore.QObject): # signal
    image_data = QtCore.pyqtSignal(np.ndarray)
    def __init__(self, camera_port=cv2.CAP_DSHOW, parent=None):
        global stopped
        super().__init__(parent)
        self.camera = cv2.VideoCapture(camera_port)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280);
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720);
        self.timer = QtCore.QBasicTimer()
        stopped = False

    def start_recording(self):
        self.timer.start(0, self)

    def timerEvent(self, event):
        global stateList, frameTime, cur_image, stopped
        save_path = r"C:\Users\38407\Desktop\Analyze"
        if (event.timerId() != self.timer.timerId()):
            return
        read, image = self.camera.read() # In case that the first captrued is black
        if read:
            if stopped:
                image = cur_image
            self.image_data.emit(image) # show image...
            cur_image = image

        frameTime = time.strftime('%H:%M:%S',time.localtime(time.time())) # time stamp

    def stop_recording(self):
        global stopped
        if stopped:
            stopped = False
        else:
            stopped = True
        

class FaceDetectionWidget(QtWidgets.QWidget): # draw rectangular
    def __init__(self, parent=None):
        super().__init__(parent)
        project_path = r"C:\Users\38407\Desktop\demo"
        modelFile = project_path + r"\res10_300x300_ssd_iter_140000.caffemodel"
        configFile = project_path + r"\deploy.prototxt"
        self.stateMap = {"0": "confused", "1": "interested", "2": "distracted", "3": "normal"}
        self.net = cv2.dnn.readNetFromCaffe(configFile, modelFile)
        self.image = QtGui.QImage()
        self._rgb = {"3": (105,105,105), "2": (255,187,0), "1": (0,191,255), "0": (50,205,50)}   # 四种颜色: grey, blue, orange, green 
        self.conf_threshold = 0.5
        rec.classifier_setup()

    def detect_faces(self, image: np.ndarray):
        (h, w) = image.shape[:2]
        qs = lambda xs : ( (len(xs) <= 1 and [xs]) or [ qs( [x for x in xs[1:] if x[0] >= xs[0][0]] ) + [xs[0]] + qs( [x for x in xs[1:] if x[0] < xs[0][0]] ) ] )[0]
        blob = cv2.dnn.blobFromImage(cv2.resize(image,(300,300)), 1.0, (300, 300), [104, 117, 123], False, False)
        self.net.setInput(blob)
        detections = self.net.forward()
        boxes = np.zeros(shape=(detections.shape[2],4))
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence < self.conf_threshold:
                continue
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            boxes[i] = box
        boxes = qs(boxes.astype("int").tolist())
        return np.array(boxes)
            

    def image_data_slot(self, image_data):
        global stateList
        boxes = self.detect_faces(image_data)
        # print(boxes)
        if stopped:
            stateList = []
        if stateList:
            for (startX, startY, endX, endY), state in zip(boxes, stateList):
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(image_data, (startX, startY), (endX, endY), self._rgb[str(state)], 4)
                cv2.putText(image_data, self.stateMap[str(state)] , (startX, y), cv2.FONT_HERSHEY_PLAIN, 3, self._rgb[str(state)], 4)
        self.image = self.get_qimage(image_data)
        if self.image.size() != self.size():
            self.setFixedSize(self.image.size())
        self.update()

    def get_qimage(self, image: np.ndarray): # y
        height, width, colors = image.shape
        bytesPerLine = 3 * width
        QImage = QtGui.QImage
        image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        image = image.rgbSwapped()
        return image

    def paintEvent(self, event): # y
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

class GetState(QtCore.QThread):
    def __init__(self, parent=None):
        super(GetState, self).__init__(parent)
        self.num = 0

    def run(self):
        global cur_image, stateList, stuNum
        while True:
            if cur_image != []:
                img_path = r"C:\Users\38407\Desktop\Analyze\frame.jpg"
                cv2.imwrite(img_path, cur_image)
                img_data = open(img_path, "rb").read() # binary
                stateList, stuNum = rec.state_creator(img_data)
            else:
                stateList = []
                stuNum = 0

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2560, 1440)
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Background,QtGui.QColor(255,255,255))
        MainWindow.setPalette(palette)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("reco.ico"),QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.thread = GetState()
        self.thread.start()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.OutterGrid = QtWidgets.QGridLayout()
        self.OutterGrid.setObjectName("OutterGrid")
        self.UpperGrid = QtWidgets.QGridLayout()
        self.UpperGrid.setObjectName("UpperGrid")
        self.LowerGrid = QtWidgets.QGridLayout()
        self.LowerGrid.setObjectName("LowerGrid")
        self.Quit = QtWidgets.QPushButton(self.centralwidget)
        self.Quit.setObjectName("Quit")
        self.Start = QtWidgets.QPushButton(self.centralwidget)
        self.Start.setObjectName("Start")
        self.Stop = QtWidgets.QPushButton(self.centralwidget)
        self.Stop.setObjectName("Stop")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.LowerGrid.addItem(spacerItem, 3, 0, 1, 7)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.LowerGrid.addItem(spacerItem1, 0, 0, 1, 7)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.LowerGrid.addItem(spacerItem2, 2, 4, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.LowerGrid.addItem(spacerItem3, 2, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.LowerGrid.addItem(spacerItem5, 2, 2, 1, 1)
        self.LowerGrid.addItem(spacerItem4, 2, 6, 1, 1)
        self.LowerGrid.addWidget(self.Start, 2, 1, 1, 1)
        self.LowerGrid.addWidget(self.Stop, 2, 3, 1, 1)
        self.LowerGrid.addWidget(self.Quit, 2, 5, 1, 1) # int r, int c, int rowspan, int columnspan
        self.OutterGrid.addLayout(self.LowerGrid, 1, 0, 1, 1)
        self.Quit.clicked.connect(MainWindow.close)

        # face recognition
        self.face_detection_widget = FaceDetectionWidget()
        # TODO: set video port
        self.record_video = RecordVideo()
        # Connect the image data signal and slot together
        image_data_slot = self.face_detection_widget.image_data_slot
        self.record_video.image_data.connect(image_data_slot)
        # connect the run button to the start recording slot
        self.Start.clicked.connect(self.record_video.start_recording)
        self.Stop.clicked.connect(self.record_video.stop_recording)
        self.UpperGrid.addWidget(self.face_detection_widget, 1, 0, 1, 1)

        self.dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.UpperGrid.addWidget(self.dynamic_canvas, 1, 1, 1, 1)
        self.addToolBar(NavigationToolbar(self.dynamic_canvas, self))
        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        self._timer = self.dynamic_canvas.new_timer(0, [(self._update_canvas, (), {})])
        self._timer.start()

        # add timeframe
        self.timeLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        self.timeLabel.setFont(font)
        self.timeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.timeLabel.setObjectName("label")
        self.UpperGrid.addWidget(self.timeLabel, 0, 0, 1, 1)
        self.timlabTimer = QtCore.QTimer()
        self.timlabTimer.timeout.connect(self._update_time)
        self.timlabTimer.start()        
        # add number of students
        self.numLabel = QtWidgets.QLabel(self.centralwidget) # timeframe
        font = QtGui.QFont()
        font.setPointSize(18)
        self.numLabel.setFont(font)
        self.numLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.numLabel.setObjectName("label")
        self.UpperGrid.addWidget(self.numLabel, 0, 1, 1, 1)
        self.numlabTimer = QtCore.QTimer()
        self.numlabTimer.timeout.connect(self._update_num)
        self.numlabTimer.start()

        self.OutterGrid.addLayout(self.UpperGrid, 0, 0, 1, 1)
        self.OutterGrid.setRowStretch(0, 3)
        self.OutterGrid.setRowStretch(1, 1)
        self.gridLayout_3.addLayout(self.OutterGrid, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def _update_canvas(self):
        global stateList
        self._dynamic_ax.clear()
        state = ['confused ', 'interested', 'distracted', 'normal  ']
        y_pos = range(len(state))
        ratio = np.zeros(4)
        if (stateList):
            for n in list(range(0,4)):
                ratio[n] = (stateList.count(n)/len(stateList))*100
            csfont = {'fontname':'Comic Sans MS'}
            self._dynamic_ax.barh(state, ratio, align='center', alpha=0.7, color=['limegreen', 'orange', 'deepskyblue', 'darkgrey'])
            self._dynamic_ax.set_xticks(np.arange(0,101,step=10))
            self._dynamic_ax.tick_params(axis='x', which='major', labelsize=14)
            self._dynamic_ax.set_yticklabels(state,fontsize=20, fontweight="bold", **csfont)
            # self._dynamic_ax.set_yticks(y_pos,state)
            self._dynamic_ax.set_xlabel('percentage %', fontsize=18, fontweight="bold", **csfont)
            self._dynamic_ax.set_title('State of Students', fontsize=40, fontweight="bold", pad=30,**csfont)
            # handles, labels = self._dynamic_ax.get_legend_handles_labels()
            # self._dynamic_ax.legend(handles[::-1], labels[::-1])
            self._dynamic_ax.spines['bottom'].set_linewidth(2);
            self._dynamic_ax.spines['left'].set_linewidth(2);
            self._dynamic_ax.spines['right'].set_linewidth(2);
            self._dynamic_ax.spines['top'].set_linewidth(2);
            self._dynamic_ax.figure.canvas.draw()

    def _update_time(self):
        global frameTime
        self.timeLabel.setText("Frame Time: " + frameTime)
    def _update_num(self):
        global stuNum
        self.numLabel.setText(str(stuNum) + " Student(s)")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", " Condition Recognition"))
        self.Start.setText(_translate("MainWindow", "Capture Start"))
        self.Quit.setText(_translate("MainWindow", "Quit"))
        self.Stop.setText(_translate("MainWindow", "Stop"))
