# output acquired from fisheye_calib, output image retains a greater number of pixels than fisheye_usage.py
# focuses on capturing one image and showing the undistorted result
import numpy as np
import cv2
import glob
from picamera import PiCamera

# current matrices to be used, must be updated bc device was shifted
K = np.array([[318.5047565963465, 0.0, 304.72174448074446], [0.0, 318.3070269260298, 234.84280567757642], [0.0, 0.0, 1.0]])
D = np.array([[-0.041193383831182505], [0.012582938251747337], [-0.026474498577198458], [0.020393209710516367]])
DIM = (480,640) # image dimensions


# takes an image path and undistorts the image with above matrices
def undistort(img_path, balance = 0.0, dim2=None, dim3 = None):
    img = cv2.imread(img_path)
    dim1 = img.shape[:2][::-1] # dim1 is the dimension of input image to undistort
    
    if not dim2:
        dim2 =dim1
        
    if not dim3:
        dim3 = dim1
        
    scaled_K = K * dim1[0] / DIM[0] # The values of K is to scale with image dimension
    scaled_K[2][2] = 1.0

    # generates a matrix to fix the output image
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K,D,dim2,np.eye(3),balance=balance)
    map1,map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K,D,np.eye(3),new_K,dim3,cv2.CV_16SC2)
    undistorted_img = cv2.remap(img,map1,map2,interpolation=cv2.INTER_LINEAR,borderMode = cv2.BORDER_CONSTANT)
    
    cv2.imshow("Undistorted frame", undistorted_img)
    cv2.waitKey(0)

# take picture from over the stove and pass it to undistort
def capture():
    camera = PiCamera()
    camera.rotation = 180
    camera.capture('/home/pi/the-rat/SW/main/shot.jpg')
    undistort('/home/pi/the-rat/SW/main/shot.jpg')

if __name__ == "__main__":
    main()
