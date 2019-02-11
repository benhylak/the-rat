#!/usr/bin/env python3
import firebase_admin
import time
from firebase_admin import credentials, db
from capture_undistorted import capture

from Stove import Stove
from Thermal import ThermalMeasure
from pot_detection import PotDetector

ITERATION_TIME = 7
cred = credentials.Certificate('/home/pi/the-rat/SW/main/ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL': 'https://the-rat-magic.firebaseio.com/'})

db = db.reference("Stove")

thermal = ThermalMeasure()
stove = Stove()
pot_detector = PotDetector()

while (True):
    
    for burner in [stove.upper_left, stove.lower_left, stove.lower_right, stove.upper_right]:
        db.child("burners").child(burner.name).set(vars(burner))

    image_path = capture()

    with open(image_path, mode="rb") as frame:
        pot_detector.update(frame, stove)

    thermal.update(stove)

    time.sleep(ITERATION_TIME)