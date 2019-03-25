#!/usr/bin/env python3
import firebase_admin
import time
import argparse
import json
from firebase_admin import credentials, db
from capture_distorted import capture
from capture_undistorted import undistort
from PIL import Image

from Stove import Stove
from Thermal import ThermalMeasure
from pot_detection import PotDetector
from boil_detect import BoilDetector
from burner_on import BurnerOnDetector
from pancake_class import PancakeClass
from ramen_class import RamenClass

ITERATION_TIME = 0.5

parser = argparse.ArgumentParser()
parser.add_argument('--detect-pots', action='store_true')
parser.add_argument('--update-time', type=float)

cred = credentials.Certificate('/home/pi/the-rat/SW/main/ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL': 'https://the-rat-magic.firebaseio.com/'})

db = db.reference("Stove")

def to_dict(obj):
    results = json.loads(json.dumps(obj, default=lambda o: o.__dict__))
    return results

def main(detect_pots, update_time):

    thermal = ThermalMeasure()
    stove = Stove()
    pot_detector = PotDetector()
    boil_detector = BoilDetector()
    burner_on = BurnerOnDetector()
    pancake_class = PancakeClass()
    ramen_class = RamenClass()

    while (True):

        original_image_path = capture()
        modified_image_path = undistort(original_image_path)
        
        for burner in [stove.upper_left, stove.lower_left, stove.lower_right, stove.upper_right]:
            db.child("burners").child(burner.name).set(to_dict(burner))
            
            if burner.recipe.name == "pancakes":
                pancake_class.update(original_image_path, stove)
            elif burner.recipe.name == "ramen":
                ramen_class.update(original_image_path, stove)


        with open(original_image_path, mode="rb") as mod_frame:
            if(detect_pots == True):
                pot_detector.update(mod_frame, stove)
            boil_detector.update(original_image_path, stove)

        thermal.update(stove)
        burner_on.update(stove)
        
        if(update_time != None):
            iteration_time = args.update_time
        else:
            iteration_time = ITERATION_TIME

        time.sleep(iteration_time)
        
if __name__ == '__main__':
        args = parser.parse_args()
        main(args.detect_pots, args.update_time)
