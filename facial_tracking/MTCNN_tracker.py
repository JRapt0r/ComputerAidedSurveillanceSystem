# Vision/face tracking libraries
import cv2
from mtcnn.mtcnn import MTCNN

# Import serial for interfacing with the Arduino
import serial



# Create connection with the Arduino
duino = serial.Serial('COM4', 115200, timeout=5)

detector = MTCNN()  # Initialize MTCNN 'detector' object

# Captures a feed from the webcam
cap = cv2.VideoCapture(0)

# Increase face detection speed through lowering the resolution
cap.set(3, 320)
cap.set(4, 240)

FRAME_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
FRAME_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

FRAME_CENTER_X = int(FRAME_WIDTH / 2)
FRAME_CENTER_Y = int(FRAME_HEIGHT / 2)

# Modifier that determines how far the face is allowed to deviate from the center
X_OFF_CENTER_LIMIT = 50
Y_OFF_CENTER_LIMIT = 38

# Declare the limits we want to adhere to in order to center the face in the image
X_HIGH_LIMIT = FRAME_CENTER_X + X_OFF_CENTER_LIMIT
X_LOW_LIMIT = FRAME_CENTER_X - X_OFF_CENTER_LIMIT

Y_HIGH_LIMIT = FRAME_CENTER_Y + Y_OFF_CENTER_LIMIT
Y_LOW_LIMIT = FRAME_CENTER_Y - Y_OFF_CENTER_LIMIT

# We want to track the position of this face every frame
# to determine if we have to move the servos faster
lastX = 0
lastY = 0

centerX = 0
centerY = 0

# Are we currently tracking or not?
tracking = False

#threading
import threading

# Determine the limits for determining big/med/small move
BIG_MOVE_LIMIT_X = 25
MED_MOVE_LIMIT_X = 15
SMALL_MOVE_LIMIT_X = 5

BIG_MOVE_LIMIT_Y = 19
MED_MOVE_LIMIT_Y = 11
SMALL_MOVE_LIMIT_Y = 4

ioPendingMessage = ""
killThreads = False

#How many faces did we detect last frame?
lastFrameFaces = 0

#We had to create a thread to handle serial communications
def ioDuinoThread():
    global tracking
    global ioPendingMessage
    global killThreads
    global lastFrameFaces
    faces = 0
    ioduino = serial.Serial('COM3', 115200, timeout=5)
    while(True):
        if(killThreads):
            break
        if ioduino.in_waiting > 0:
            if "toggleTracking" in str(ioduino.readline()):
                tracking = not tracking
                ioduino.flush()
        if(lastFrameFaces != faces):
            temp = "faceData faces: " + str(lastFrameFaces)
            print(temp)
            faces = lastFrameFaces
            ioduino.write(temp.encode())
            ioduino.flush()
        if(ioPendingMessage != ""):
            ioduino.write(ioPendingMessage.encode())
            ioduino.flush
            ioPendingMessage = ""


serialThread = threading.Thread(target = ioDuinoThread)
serialThread.start()

def sendToSerial(data, board):
    global ioPendingMessage
    global duino
    if (board == 1):
        duino.write(data.encode())
    if (board == 2):
        ioPendingMessage = data
    duino.flush()
    


def determineMoves(centerX, centerY):

    global lastX
    global lastY
    global lastMessage

    serialString = ""

    if (centerY < Y_LOW_LIMIT):
        serialString += "down"
    elif (centerY > Y_HIGH_LIMIT):
        serialString += "up"

    if (centerX < X_LOW_LIMIT):
        serialString += "left"
    elif (centerX > X_HIGH_LIMIT):
        serialString += "right"

    # Determine how far the face has moved
    if (centerX - lastX > BIG_MOVE_LIMIT_X or -(centerX - lastX) > BIG_MOVE_LIMIT_X):
        serialString += "bigx"
    elif (centerX - lastX > MED_MOVE_LIMIT_X or -(centerX - lastX) > MED_MOVE_LIMIT_X):
        serialString += "medx"
    elif (centerX - lastX > SMALL_MOVE_LIMIT_X or -(centerX - lastX) > SMALL_MOVE_LIMIT_X):
        serialString += "smallx"

    if (centerY - lastY > BIG_MOVE_LIMIT_Y or -(centerY - lastY) > BIG_MOVE_LIMIT_Y):
        serialString += "bigy"
    elif (centerY - lastY > MED_MOVE_LIMIT_Y or -(centerY - lastY) > MED_MOVE_LIMIT_Y):
        serialString += "medy"
    elif ((centerY - lastY > SMALL_MOVE_LIMIT_Y or centerY - lastY > SMALL_MOVE_LIMIT_Y)):
        serialString += "smally"

    # If we've made no moves, our arduino camera is centered, so we should tell it that
    # ALL STRINGS BEGINNING WITH DUINO2 ARE ONLY HANDELED BY THE SECOND ARDUINO
    if serialString == "":
        serialString = str("DUINO2 toggleLED\n")
        sendThread = threading.Thread(target = sendToSerial, args=(serialString,2))
        sendThread.start()
    else:
        sendThread = threading.Thread(target = sendToSerial, args=(serialString,1))
        sendThread.start()

    lastMessage = serialString

    lastY = centerY
    lastX = centerX


while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Use MTCNN to detect faces
    result = detector.detect_faces(frame)

    if result != [] and tracking:
        for person in result:
            bounding_box = person['box']

            # Retrieve x, y, w, h coordinate data from the 'bounding_box' array
            x = bounding_box[0]
            y = bounding_box[1]
            w = bounding_box[2]
            h = bounding_box[3]

            # Display an orange rectangle around face detected
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 155, 255), 2)

            # Point for center of image
            # For each face detected, add to the value
            # These will be average later
            centerX = int(x + (w / 2))
            centerY = int(y + (h / 2))
            determineMoves(centerX, centerY)

        # Send to the second arduino the number of faces detected
    
    lastFrameFaces = len(result)
    cv2.imshow('frame', cv2.flip(frame, 1))

    # Waits for the "q" key to quite the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        killThreads = True
        break

# Releases the capture
cap.release()
cv2.destroyAllWindows()
