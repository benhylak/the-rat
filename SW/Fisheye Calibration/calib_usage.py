import numpy as np
import cv2
import yaml

with open('parameters.yaml') as f:
    loadeddict = yaml.load(f)
    
mtxloaded = loadeddict.get('camera_matrix')
distloaded = loadeddict.get('dist_coeff')

img = cv2.imread("/home/pi/the-rat/SW/Fisheye Calibration/Chess_Stove/image0.jpg")
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtxloaded,distloaded, (w,h), 0, (w,h))

mapx, mapy = cv2.initUndistortRectifyMap(mtxloaded,distloaded,None,newcameramtx,(w,h),5)

dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)

x,y,w,h = roi
#dst = dst[y:y+h, x:x+h] #produces 0 KB jpg

h, w = dst.shape[:2]
print(h)
print("\n")
print(w)
cv2.imwrite('photo3.jpg',dst)

# debug statements
print(mtxloaded) #kl
print(distloaded) #d
print("\n")
print(newcameramtx)