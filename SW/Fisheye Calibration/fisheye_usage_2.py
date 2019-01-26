# output acquired from fisheye_calib, output image retains a greater number of pixels than fisheye_usage.py
import numpy as np
import cv2
import glob

# arrays acquired from fisheye_calib with the checkerboard images taken at home
#D|M=(900, 1600)
#K=[[797.2587334291815, 0.0, 833.6012053603583], [0.0, 795.5207655206569, 457.3697345987934], [0.0, 0.0, 1.0]]
#D=[[-0.05741254296793641], [0.28860922196944333], [-1.2604874813718503], [1.6910633425534995]]

K = np.array([[797.2587334291815, 0.0, 833.6012053603583], [0.0, 795.5207655206569, 457.3697345987934], [0.0, 0.0, 1.0]])
D = np.array([[-0.05741254296793641], [0.28860922196944333], [-1.2604874813718503], [1.6910633425534995]])
DIM = (1600,900) # image dimensions

def undistort(img_path, balance = 0.0, dim2=None, dim3 = None):
    img = cv2.imread(img_path)
    dim1 = img.shape[:2][::-1] # dim1 is the dimension of input image to undistort
    
   # assert dim1[0]/dim1[1] == DIM[0]/DIM[1], "image to undistort needs to have the same aspect ratio as the ones used in calibration"
    
    if not dim2:
        dim2 =dim1
        
    if not dim3:
        dim3 = dim1
        
    scaled_K = K * dim1[0] / DIM[0] # The values of K is to scale with image dimension
    scaled_K[2][2] = 1.0
    
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K,D,dim2,np.eye(3),balance=balance)
    map1,map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K,D,np.eye(3),new_K,dim3,cv2.CV_16SC2)
    undistorted_img = cv2.remap(img,map1,map2,interpolation=cv2.INTER_LINEAR,borderMode = cv2.BORDER_CONSTANT)
    
    cv2.imwrite("/home/pi/Undistorted Images/undistorted_stove_img.jpg",undistorted_img)


#images = glob.glob('/home/pi/Stove/*.jpg')
 
#for fname in images:
 #   undistort(fname)
undistort("/home/pi/Stove/image0.jpg")