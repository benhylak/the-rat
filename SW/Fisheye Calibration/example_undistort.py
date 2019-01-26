import numpy as np
import cv2
import glob

a = np.load('C.npz')

img = cv2.imread('image11.jpg')
h, w = img.shape[:2]
newcameratx, roi = cv2.getOptimalNewCameraMatrix(a['mtx'],a['dist'],(w,h),1,(w,h))

dst = cv2.undistort(img,a['mtx'],a['dist'],None,newcameratx)

x,y,w,h, = roi
dst = dst[y:y+h,x:x+w]
cv2.imwrite('cal2.png',dst)

cv2.destroyAllWindows()
                   
