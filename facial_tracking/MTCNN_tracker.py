# Vision/face tracking libraries
import cv2
from mtcnn.mtcnn import MTCNN

# Import serial for interfacing with the Arduino
import serial

# Create connection with the Arduino
duino = serial.Serial('COM6', 115200, timeout=1)
ioduino = serial.Serial('COM4', 115200, timeout=1)

detector = MTCNN()  # Initialize MTCNN 'detector' object

# Captures a feed from the webcam
cap = cv2.VideoCapture(1)

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


# Determine the limits for determining big/med/small move
BIG_MOVE_LIMIT_X = 25
MED_MOVE_LIMIT_X = 15
SMALL_MOVE_LIMIT_X = 5

BIG_MOVE_LIMIT_Y = 19
MED_MOVE_LIMIT_Y = 11
SMALL_MOVE_LIMIT_Y = 4

lastMessage = ""


def sendToSerial(data, board):
    if (board == 1):
        duino.write(data.encode())
    if (board == 2):
        ioduino.write(data.encode())


def determineMoves(centerX, centerY):

    global lastX
    global lastY
    global lastMessage

    serialString = ""

    print(centerX - lastX)

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
        print("big x move")
        serialString += "bigx"
    elif (centerX - lastX > MED_MOVE_LIMIT_X or -(centerX - lastX) > MED_MOVE_LIMIT_X):
        print("med x move")
        serialString += "medx"
    elif (centerX - lastX > SMALL_MOVE_LIMIT_X or -(centerX - lastX) > SMALL_MOVE_LIMIT_X):
        print("small x move")
        serialString += "smallx"

    if (centerY - lastY > BIG_MOVE_LIMIT_Y or -(centerY - lastY) > BIG_MOVE_LIMIT_Y):
        print("big y move")
        serialString += "bigy"
    elif (centerY - lastY > MED_MOVE_LIMIT_Y or -(centerY - lastY) > MED_MOVE_LIMIT_Y):
        print("med y move")
        serialString += "medy"
    elif ((centerY - lastY > SMALL_MOVE_LIMIT_Y or centerY - lastY > SMALL_MOVE_LIMIT_Y)):
        print("small y move")
        serialString += "smally"

    # If we've made no moves, our arduino camera is centered, so we should tell it that
    # ALL STRINGS BEGINNING WITH DUINO2 ARE ONLY HANDELED BY THE SECOND ARDUINO
    if serialString == "":
        print("bck dick")
        serialString = str("DUINO2 toggleLED\n")
        sendToSerial(serialString, 2)
    else:
        sendToSerial(serialString, 1)

    lastMessage = serialString

    lastY = centerY
    lastX = centerX


while (True):

    # If we've recieved a string from the arduino
    if ioduino.in_waiting > 0:
        if "toggleTracking" in str(ioduino.readline()):
            tracking = not tracking
            print("Tracking")

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
        sendToSerial("DUINO2 faceData faces: " + str(len(result)), 2)

    cv2.imshow('frame', cv2.flip(frame, 1))

    # Waits for the "q" key to quite the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Releases the capture
cap.release()
cv2.destroyAllWindows()
