import numpy as np
import cv2
import glob
import yaml
import os

#termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)

# Checkerboard inner corner size
CHECKERBOARD = (6,9)

calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND+cv2.fisheye.CALIB_FIX_SKEW
#calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_FIX_SKEW
#prepare object points and image points from all the images
objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1],3),np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0],0:CHECKERBOARD[1]].T.reshape(-1,2)

# Arrays to store objects and image points from all the images
objpoints = [] #3d point in a real world space
imgpoints = [] #2d points in image plane

#searches for all jpgs within its folder
images = glob.glob('/home/pi/the-rat/SW/Fisheye Calibration/Chess_Stove_3/*.jpg')
 
for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #image_shape= img.shape[:2]
    #find corners of the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    
    # If found, add object points, image points after refining them
    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),criteria)
        imgpoints.append(corners2)

N_OK=len(objpoints)
K=np.zeros((3,3))
D=np.zeros((4,1))
rvecs=[np.zeros((1,1,3),dtype=np.float64) for i in range (N_OK)]
tvecs=[np.zeros((1,1,3),dtype=np.float64) for i in range (N_OK)]

rms, _, _, _, _ = \
     cv2.fisheye.calibrate(
         objpoints,imgpoints,
         gray.shape[::-1],
         K,
         D,
         rvecs,
         tvecs,
         calibration_flags,
         (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,30,1e-6)
    )

print( "Found: " + str(N_OK) + " valid images for calib")

print("DIM=" + str(img.shape[:2])) #dimensions of images
print("K=" + str(K.tolist()))
print("D=" + str(D.tolist()))
