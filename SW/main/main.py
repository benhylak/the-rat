import firebase_admin
import time
from firebase_admin import credentials, db
from capture_undistorted import capture

from Stove import Stove
from Thermal import ThermalMeasure

ITERATION_TIME = 7
cred = credentials.Certificate('./ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL': 'https://the-rat-magic.firebaseio.com/'})

db = db.reference("Stove")

thermal = ThermalMeasure()
stove = Stove()

while (True):
    
    for burner in [stove.upper_left, stove.lower_left, stove.lower_right, stove.upper_right]:
        db.child("burners").child(burner.name).set(vars(burner))

    thermal.update(stove)

    image_path = capture()

    time.sleep(ITERATION_TIME)
