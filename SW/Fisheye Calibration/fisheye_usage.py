# from the fisheye tutorial but loses some pixels, produces undistorted10.jpg
import numpy as np
import cv2
    
# arrays acquired from fisheye_calib with the checkerboard images taken at home
#D|M=(900, 1600)
#K=[[797.2587334291815, 0.0, 833.6012053603583], [0.0, 795.5207655206569, 457.3697345987934], [0.0, 0.0, 1.0]]
#D=[[-0.05741254296793641], [0.28860922196944333], [-1.2604874813718503], [1.6910633425534995]]

K = np.array([[797.2587334291815, 0.0, 833.6012053603583], [0.0, 795.5207655206569, 457.3697345987934], [0.0, 0.0, 1.0]])
D = np.array([[-0.05741254296793641], [0.28860922196944333], [-1.2604874813718503], [1.6910633425534995]])
DIM = (900,1600) # image dimensions

img = cv2.imread("/home/pi/Stove/image0.jpg")
h, w = img.shape[:2]

mapx, mapy = cv2.fisheye.initUndistortRectifyMap(K,D,np.eye(3),K,DIM,cv2.CV_16SC2)
undistorted_img = cv2.remap(img,mapx,mapy,interpolation=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)

#cv2.imshow("undistorted",undistorted_img)
# saves the undistorted image
cv2.imwrite("undistorted_stove_f1.jpg",undistorted_img)
cv2.waitKey(0)

cv2.destroyAllWindows()
    