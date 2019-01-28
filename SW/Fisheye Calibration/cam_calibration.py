#based on the opencv tutorial, undistorted image ends up lloing more distorted

import numpy as np
import cv2
import glob
import yaml

#termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Checkerboard size
CHECKERBOARD = (6,9)

#prepare object points and image points from all the images
objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1],3),np.float32)
objp[:,:2] = np.mgrid[0:CHECKERBOARD[1],0:CHECKERBOARD[0]].T.reshape(-1,2)

# Arrays to store objects and image points from all the images
objpoints = [] #3d point in a real world space
imgpoints = [] #2d points in image plane

images = glob.glob('/home/pi/the-rat/SW/Fisheye Calibration/Chess_Stove/*.jpg')
 
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #find corners of the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (CHECKERBOARD[1],CHECKERBOARD[0]), None)
    
    # If found, add object points, image points after refining them
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        #Draw and display the cortners
        img = cv2.drawChessboardCorners(img, (CHECKERBOARD[1],CHECKERBOARD[0]),corners2,ret)
    cv2.imshow('img',img)
    cv2.waitKey(50)

cv2.destroyAllWindows()
ret,mtx,dist,rvecs,tvecs = cv2.calibrateCamera(objpoints,imgpoints,gray.shape[::-1],None,None)

# trying something new, saving the matrices to use in another py file
data = {'camera_matrix' : np.asarray(mtx), 'dist_coeff': np.asarray(dist)}

with open("parameters.yaml","w") as f:
    yaml.dump(data,f)

mean_error = 0
tot_error = 0

for i in range(len(objpoints)):
    imgpoints2, _  = cv2.projectPoints(objpoints[i],rvecs[i],tvecs[i],mtx,dist)
    error = cv2.norm(imgpoints[i],imgpoints2,cv2.NORM_L2)/len(imgpoints2)
    tot_error+= error
    
print( "Tot error:", tot_error/len(objpoints))          