# output acquired from fisheye_calib, output image retains a greater number of pixels than fisheye_usage.py
# Iterates through Chess_Stove_3 and shows a screen with the undistorted versions
import numpy as np
import cv2
import glob

# arrays acquired from fisheye_calib with the checkerboard images taken at home
#D|M=(900, 1600)
#K=[[797.2587334291815, 0.0, 833.6012053603583], [0.0, 795.5207655206569, 457.3697345987934], [0.0, 0.0, 1.0]]
#D=[[-0.05741254296793641], [0.28860922196944333], [-1.2604874813718503], [1.6910633425534995]]

# first attempt with the mounted camera
#K = np.array([[309.73063017177265, 0.0, 305.15838341687373], [0.0, 310.14817571047683, 233.55994672848328], [0.0, 0.0, 1.0]])
#D = np.array([[-0.014947211301413587], [-0.06846319389144614], [0.09750581352254294], [-0.0536059041795989]])
#DIM = (480,640) # image dimensions

# second attempt with more edge shots, current matrices
K = np.array([[318.5047565963465, 0.0, 304.72174448074446], [0.0, 318.3070269260298, 234.84280567757642], [0.0, 0.0, 1.0]])
D = np.array([[-0.041193383831182505], [0.012582938251747337], [-0.026474498577198458], [0.020393209710516367]])
DIM = (480,640) # image dimensions

def undistort(img_path, i, balance = 0.0, dim2=None, dim3 = None):
    img = cv2.imread(img_path)
    dim1 = img.shape[:2][::-1] # dim1 is the dimension of input image to undistort
    
    if not dim2:
        dim2 =dim1
        
    if not dim3:
        dim3 = dim1
        
    scaled_K = K * dim1[0] / DIM[0] # The values of K is to scale with image dimension
    scaled_K[2][2] = 1.0
    
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K,D,dim2,np.eye(3),balance=balance)
    map1,map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K,D,np.eye(3),new_K,dim3,cv2.CV_16SC2)
    undistorted_img = cv2.remap(img,map1,map2,interpolation=cv2.INTER_LINEAR,borderMode = cv2.BORDER_CONSTANT)
    
    #cv2.imwrite("/home/pi/Undistorted Images/u%s.jpg" % i,undistorted_img)
    cv2.imshow("/home/pi/Undistorted Images/u%s.jpg", undistorted_img)
    cv2.waitKey(0)

images = glob.glob('/home/pi/the-rat/SW/Fisheye Calibration/Chess_Stove_3/*.jpg')
i = 0
for fname in images:
    undistort(fname, i)
    i = i + 1
#undistort("/home/pi/the-rat/SW/Fisheye Calibration/Chess_Stove_3/mounted_sec12.jpg")
