from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180
camera.start_preview()

for i in range(25):
    sleep(10)
    camera.capture('/home/pi/Chess_Stove/mounted_sec%s.jpg' % i)

camera.stop_preview()
