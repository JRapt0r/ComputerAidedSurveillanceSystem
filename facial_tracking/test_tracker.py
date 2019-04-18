# Reference https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_objdetect/py_face_detection/py_face_detection.html

import numpy as np
import cv2

#import serial for interfacing with arduino
import serial

# create connection with arduino
duino = serial.Serial('COM4', 115200, timeout = 0.050)

# Loads the face cascades, uses "haarcascade" templates for better accuracy
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
profile_cascade = cv2.CascadeClassifier('haarcascade_profileface.xml')

# Captures a feed from the webcam
cap = cv2.VideoCapture(0)

# Declare the limits we want to adhere to in order to center the face in the image
X_HIGH_LIMIT = 176
X_LOW_LIMIT = 150

Y_HIGH_LIMIT = 100
Y_LOW_LIMIT = 75


def handleSerial(x1,y1,w,h):
    serialString = ""
    pointX = x1 + (w/2)
    pointY = y1 + (h/2)

    if(pointX > X_HIGH_LIMIT):
        serialString += "right"
    elif(pointX < X_LOW_LIMIT):
        serialString += "left"

    if(pointY > Y_HIGH_LIMIT):
        serialString += "down"
    elif(pointY < Y_LOW_LIMIT):
        serialString += "up"
    
    duino.write(serialString.encode())
    

while (True):
    if(duino.in_waiting > 0):
        print(duino.readline())

    ret, frame = cap.read()
	
    # Converts the captured frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	
    # Looks for faces using the face cascade data
    faces = face_cascade.detectMultiScale(gray, 1.125, 5)
    profiles = profile_cascade.detectMultiScale(gray, 1.1, 5)

    for (x, y, w, h) in faces:		
        cv2.rectangle(gray, (x, y), (x + w, y + h), (255, 0, 0), 2)
        handleSerial(x,y,w,h)


    if (len(faces) == 0): # only looks for profiles if a face hasn't been found
        for (px, py, pw, ph) in profiles:
            cv2.rectangle(gray,(px,py),(px+pw,py+ph),(0,255,0),2)
            handleSerial(px,py,pw,ph)

	
    cv2.imshow('frame',gray)


	# Waits for the "q" key to quite the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Releases the capture
cap.release()
cv2.destroyAllWindows()