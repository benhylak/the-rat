import cv2
import numpy as np

# create vidcapture object
cap = cv2.VideoCapture(0)

# check if successfully opened
if(cap.isOpened() == False):
    print("Could not open video stream")

# Read until quit
while(cap.isOpened()):
    # capture frame by frame
    ret, frame = cap.read()
    if ret == True:

        # display the resulting frame
        cv2.imshow('Frame', frame)

        # press Q on keyboard to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    else:
        break

cap.release()
cv2.destroyAllWindows()
