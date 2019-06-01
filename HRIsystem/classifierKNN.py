#coding:utf-8
import numpy as np
'''
data: features
label: according label
'''
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib

def createDataset():
	filepath1 = r"\conf.csv" # 0
	filepath2 = r"\int.csv" # 1
	filepath3 = r"\dis.csv" # 2
	filepath4 = r"\nor.csv" # 2
	face_X1 = np.loadtxt(open(filepath1,"rb"),delimiter=",",skiprows=0)
	face_X2 = np.loadtxt(open(filepath2,"rb"),delimiter=",",skiprows=0) 
	face_X3 = np.loadtxt(open(filepath3,"rb"),delimiter=",",skiprows=0) 
	face_X4 = np.loadtxt(open(filepath4,"rb"),delimiter=",",skiprows=0) 
	face_X = np.concatenate((face_X1, face_X2, face_X3, face_X4), axis=0)
	data = face_X
	list_y = [0]*50 + [1]*50 + [2]*50 + [3]*50
	face_y = np.array(list_y)
	labels = face_y
	return data,labels
'''
classifier
'''
def train(): 
	data, labels = createDataset()
	divider = int(len(labels)*0.2)
	face_X = data
	face_y = labels
	indices = np.random.permutation(len(face_X))
	#training
	face_X_train = face_X[indices[:-divider]]
	# print ((face_X_train))
	face_y_train = face_y[indices[:-divider]]
	# print (type(face_y_train))
	#testing
	face_X_test  = face_X[indices[-divider:]]
	face_y_test  = face_y[indices[-divider:]]

	knn = KNeighborsClassifier()
	knn.fit(face_X_train,face_y_train)
	joblib.dump(knn, "train_knn.m")
	# return knn, face_X_test, face_y_test

def classify(inX):
	classifier = joblib.load("train_knn.m")
	prediction = classifier.predict(inX)
	return prediction

if __name__ == '__main__':

	data,labels = createDataset()
	classifier, face_X_test, face_y_test = train(data, labels)

	prediction = classify(classifier, face_X_test)
	print ("KNN accuracy:")
	print (accuracy_score(prediction,face_y_test))
