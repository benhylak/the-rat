#!/usr/bin/env python3
import firebase_admin
import time
import argparse
from firebase_admin import credentials, db
from capture_undistorted import capture

from Stove import Stove
from Thermal import ThermalMeasure
from pot_detection import PotDetector

ITERATION_TIME = 0.5

parser = argparse.ArgumentParser()
parser.add_argument('--detect-pots', action='store_true')
parser.add_argument('--update-time', type=int)

cred = credentials.Certificate('/home/pi/the-rat/SW/main/ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL': 'https://the-rat-magic.firebaseio.com/'})

db = db.reference("Stove")

def main(detect_pots, update_time):

    thermal = ThermalMeasure()
    stove = Stove()
    pot_detector = PotDetector()

    while (True):
        
        for burner in [stove.upper_left, stove.lower_left, stove.lower_right, stove.upper_right]:
            db.child("burners").child(burner.name).set(vars(burner))

        image_path = capture()

        with open(image_path, mode="rb") as frame:
            if(detect_pots == True):
                pot_detector.update(frame, stove)

        thermal.update(stove)
        
        if(update_time != None):
            iteration_time = args.update_time
        else:
            iteration_time = ITERATION_TIME

        time.sleep(iteration_time)
        
if __name__ == '__main__':
        args = parser.parse_args()
        main(args.detect_pots, args.update_time)