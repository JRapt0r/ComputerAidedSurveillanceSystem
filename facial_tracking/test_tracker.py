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

#Let's track the position of the servo on this end too
panServo = 90
tiltServo = 90

FRAME_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
FRAME_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

FRAME_CENTER_X = int(FRAME_WIDTH / 2)
FRAME_CENTER_Y = int(FRAME_HEIGHT / 2)

#modifier that determines how far the face is allowed to deviate from the center
OFF_CENTER_LIMIT = 50

# Declare the limits we want to adhere to in order to center the face in the image
X_HIGH_LIMIT = FRAME_CENTER_X + OFF_CENTER_LIMIT
X_LOW_LIMIT = FRAME_CENTER_X - OFF_CENTER_LIMIT

Y_HIGH_LIMIT = FRAME_CENTER_Y + OFF_CENTER_LIMIT
Y_LOW_LIMIT = FRAME_CENTER_Y - OFF_CENTER_LIMIT

def determineMoves(centerX, centerY):
    global panServo
    global tiltServo
    serialString = ""

    if(centerY < Y_LOW_LIMIT):
        serialString += "down"
        panServo = panServo - 1
    elif(centerY > Y_HIGH_LIMIT):
        serialString += "up"
        panServo = panServo + 1

    if(centerX < X_LOW_LIMIT):
        serialString += "left"
        tiltServo = tiltServo - 1
    elif(centerX > X_HIGH_LIMIT):
        serialString += "right"
        tiltServo = tiltServo + 1

    printString = "Pan servo: " + str(panServo) + ", " + "Tilt servo: " + str(tiltServo)
    print(printString)

    sendToSerial(serialString) 

def sendToSerial(data):
    duino.write(data.encode())
    

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

        # I want to draw a line on the center of the face
        pt1x = int(x + (w / 2) + 5)
        pt1y = int(y + (h / 2) + 5)

        pt2x = int(x + (w / 2) - 5)
        pt2y = int(y + (h / 2) - 5)

        # Point for center of image
        centerX = int(x + (w / 2))
        centerY = int(y + (h / 2))

        cv2.line(gray,(pt1x,pt2y),(pt2x,pt1y),(255,0,0),3)

        determineMoves(centerX,centerY)


    if (len(faces) == 0): # only looks for profiles if a face hasn't been found
        for (px, py, pw, ph) in profiles:
            cv2.rectangle(gray,(px,py),(px+pw,py+ph),(0,255,0),2)

            # I want to draw a line on the center of the face
            pt1x = int(px + (pw / 2) + 5)
            pt1y = int(py + (ph / 2) + 5)

            pt2x = int(px + (pw / 2) - 5)
            pt2y = int(py + (ph / 2) - 5)

            # Point for center of image
            centerX = int(px + (pw / 2))
            centerY = int(py + (ph / 2))

            cv2.line(gray,(pt1x,pt2y),(pt2x,pt1y),(255,0,0),3)

            determineMoves(centerX,centerY)

	
    cv2.imshow('frame',gray)


	# Waits for the "q" key to quite the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Releases the capture
cap.release()
cv2.destroyAllWindows()