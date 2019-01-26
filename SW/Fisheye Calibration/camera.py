from picamera import PiCamera
from time import sleep

camera = PiCamera()

#camera.rotation = 180
camera.start_preview()

for i in range(10):
    sleep(10)
    camera.capture('/home/pi/Stove/image%s.jpg' % i)

camera.stop_preview()
