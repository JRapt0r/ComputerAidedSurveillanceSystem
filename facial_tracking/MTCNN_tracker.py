# Vision/face tracking libraries
import cv2
from mtcnn.mtcnn import MTCNN

# Import serial for interfacing with arduino
import serial

# create connection with arduino
duino = serial.Serial('COM6', 115200, timeout=0.05)
detector = MTCNN()  # Start MTCNN

# Captures a feed from the webcam
cap = cv2.VideoCapture(1)  # my laptop's built in webcam is on input 0

# Speed up face detection by lowering capture resolution
cap.set(3, 320)
cap.set(4, 240)

# Let's track the position of the servo on this end too
panServo = 90
tiltServo = 90

FRAME_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
FRAME_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

FRAME_CENTER_X = int(FRAME_WIDTH / 2)
FRAME_CENTER_Y = int(FRAME_HEIGHT / 2)

# modifier that determines how far the face is allowed to deviate from the center
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

# Determine the limits for determining big/med/small move
BIG_MOVE_LIMIT_X = 25
MED_MOVE_LIMIT_X = 15

BIG_MOVE_LIMIT_Y = 19
MED_MOVE_LIMIT_Y = 11


def determineMoves(centerX, centerY):
    global panServo
    global tiltServo
    global lastX
    global lastY
    serialString = ""
    print(centerX - lastX)

    if(centerY < Y_LOW_LIMIT):
        serialString += "down"
    elif(centerY > Y_HIGH_LIMIT):
        serialString += "up"

    if(centerX < X_LOW_LIMIT):
        serialString += "left"
    elif(centerX > X_HIGH_LIMIT):
        serialString += "right"

    # Determine how far our face has moved
    if(centerX - lastX > BIG_MOVE_LIMIT_X or -(centerX - lastX) > BIG_MOVE_LIMIT_X):
        print("big x move")
        serialString += "bigx"
    elif(centerX - lastX > MED_MOVE_LIMIT_X or -(centerX - lastX) > MED_MOVE_LIMIT_X):
        print("med x move")
        serialString += "medx"
    else:
        print("small x move")
        serialString += "smallx"

    if(centerY - lastY > BIG_MOVE_LIMIT_Y or -(centerY - lastY) > BIG_MOVE_LIMIT_Y):
        print("big y move")
        serialString += "bigy"
    elif(centerY - lastY > MED_MOVE_LIMIT_Y or -(centerY - lastY) > MED_MOVE_LIMIT_Y):
        print("med y move")
        serialString += "medy"
    else:
        print("small y move")
        serialString += "smally"

    sendToSerial(serialString)

    lastY = centerY
    lastX = centerX


def sendToSerial(data):
    duino.write(data.encode())


while (True):
    if(duino.in_waiting > 0):
        print(duino.readline())

    # Capture frame-by-frame
    ret, frame = cap.read()

    # Use MTCNN to detect faces
    result = detector.detect_faces(frame)
    if result != []:
        for person in result:
            bounding_box = person['box']
            keypoints = person['keypoints']

            x = bounding_box[0]
            y = bounding_box[1]
            w = bounding_box[2]
            h = bounding_box[3]

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 155, 255), 2)

            ''' Code for drawing other keypoints on the face
            cv2.circle(frame,(keypoints['left_eye']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['right_eye']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['nose']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['mouth_left']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['mouth_right']), 2, (0,155,255), 2)
            '''

            # I want to draw a line on the center of the face
            pt1x = int(x + (w / 2) + 5)
            pt1y = int(y + (h / 2) + 5)

            pt2x = int(x + (w / 2) - 5)
            pt2y = int(y + (h / 2) - 5)

            # Point for center of image
            centerX = int(x + (w / 2))
            centerY = int(y + (h / 2))

            cv2.line(frame, (pt1x, pt2y), (pt2x, pt1y), (255, 0, 0), 3)

            determineMoves(centerX, centerY)

    cv2.imshow('frame', cv2.flip(frame, 1))

    # Waits for the "q" key to quite the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Releases the capture
cap.release()
cv2.destroyAllWindows()
