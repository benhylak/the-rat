import firebase_admin
import time
from firebase_admin import credentials, db

from Stove import Stove
from Thermal import Thermal

cred = credentials.Certificate('./ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL': 'https://the-rat-magic.firebaseio.com/'})

db = db.reference("Stove")

thermal = Thermal()
stove = Stove()

while (True):
    
    thermal.update(stove)
    
    for burner in [stove.upper_left, stove.lower_left, stove.lower_right, stove.upper_right]:
        db.child("burners").child(burner.name).set(vars(burner))

    time.sleep(3)
