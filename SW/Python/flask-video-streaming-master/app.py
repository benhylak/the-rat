#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_pi import Camera
    from camera import CameraThermal

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def genPi(camera):
    """Video streaming generator function."""
    while True:
        camera.resolution = (640,480)
        camera.framerate = 60
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def genThermal(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/reboot/', methods = ['POST'])
def rebootPi():
    """Reboots Pi on button click"""
    os.system('reboot')

@app.route('/stopcamera/', methods = ['POST'])
def stopCamera():
    """Releases PiCam from webpage process allowing for other programs to be used"""
    return Camera.closePiCam()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(genPi(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_thermal')
def video_feed_thermal():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(genThermal(CameraThermal()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
