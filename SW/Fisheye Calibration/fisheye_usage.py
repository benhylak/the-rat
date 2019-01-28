# from the fisheye tutorial but loses some pixels
# iterates through the Chess_Stove_3 folder and displays he undistorted results
import numpy as np
import cv2
import glob
    
# arrays acquired from fisheye_calib with the checkerboard images taken at home
#D|M=(900, 1600)
#K=[[797.2587334291815, 0.0, 833.6012053603583], [0.0, 795.5207655206569, 457.3697345987934], [0.0, 0.0, 1.0]]
#D=[[-0.05741254296793641], [0.28860922196944333], [-1.2604874813718503], [1.6910633425534995]]
# acquired from initial mounted position
#K = np.array([[318.6024702032758, 0.0, 302.1276192782998], [0.0, 318.7893139303407, 235.40325417421198], [0.0, 0.0, 1.0]])
#D = np.array([[-0.06051044155029906], [0.07007181280420602], [-0.07739202974707016], [0.027078132125124794]])
#DIM = (480,640) # image dimensions
# the most recent matrices being used

K = np.array([[318.5047565963465, 0.0, 304.72174448074446], [0.0, 318.3070269260298, 234.84280567757642], [0.0, 0.0, 1.0]])
D = np.array([[-0.041193383831182505], [0.012582938251747337], [-0.026474498577198458], [0.020393209710516367]])
DIM = (480,640) # image dimensions

def undistort(image_path):
    #img = cv2.imread("/home/pi/the-rat/SW/Fisheye Calibration/Chess_Stove_3/mounted_sec12.jpg")
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    mapx, mapy = cv2.fisheye.initUndistortRectifyMap(K,D,np.eye(3),K,DIM,cv2.CV_16SC2)
    undistorted_img = cv2.remap(img,mapx,mapy,interpolation=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)

    cv2.imshow("undistorted",undistorted_img)
    # saves the undistorted image
    #cv2.imwrite("ex.jpg",undistorted_img)
    cv2.waitKey(0)

images = glob.glob("/home/pi/the-rat/SW/Fisheye Calibration/Chess_Stove_3/*.jpg")

for fname in images:
    undistort(fname)
    
cv2.destroyAllWindows()
    
