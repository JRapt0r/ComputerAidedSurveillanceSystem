import cv2
from mtcnn.mtcnn import MTCNN

detector = MTCNN()

# Captures a feed from the webcam
cap = cv2.VideoCapture(0)

while True:
    #Capture frame-by-frame
    ret, frame = cap.read()
    
    #Use MTCNN to detect faces
    result = detector.detect_faces(frame)
    if result != []:
        for person in result:
            bounding_box = person['box']
            keypoints = person['keypoints']
    		
    		#'''
            cv2.rectangle(frame,
                          (bounding_box[0], bounding_box[1]),
                          (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
                          (0,155,255),
                          2)

            cv2.circle(frame,(keypoints['left_eye']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['right_eye']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['nose']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['mouth_left']), 2, (0,155,255), 2)
            cv2.circle(frame,(keypoints['mouth_right']), 2, (0,155,255), 2)
            #'''

            print(bounding_box[0], bounding_box[1]) # Print x,y coordinates of face detected
    
    cv2.imshow('frame',cv2.flip(frame,1))

    # Waits for the "q" key to quite the program
    if cv2.waitKey(1) &0xFF == ord('q'):
        break

# Releases the capture
cap.release()
cv2.destroyAllWindows()