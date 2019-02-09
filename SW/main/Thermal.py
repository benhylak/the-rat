from Adafruit_AMG88xx import Adafruit_AMG88xx
import Stove
import pygame
import os
import math
import time
from time import sleep

import numpy as np
from scipy.interpolate import griddata

from colour import Color

class ThermalMeasure:

    def __init__(self):

        self.TEMPON = 45
        #low range of the sensor (this will be blue on the screen)
        self.MINTEMP = 18

        #high range of the sensor (this will be red on the screen)
        self.MAXTEMP = 100
        
        #initialize the sensor
        self.sensor = Adafruit_AMG88xx()
        
    def update(self, stove):

        #read the pixels
        pixels = self.sensor.readPixels()

        #split the display into 4 parts to represent each burner
        ary1 = pixels[:int(len(pixels)/2)]
        ary2 = pixels[int(len(pixels)/2):]
        burner1 = ary1[:int(len(ary1)/2)]
        burner2 = ary1[int(len(ary1)/2):]
        burner3 = ary2[:int(len(ary2)/2)]
        burner4 = ary2[int(len(ary2)/2):]

        #detect if a burner is on based on the average temperature
        avg1 = sum(burner1)/len(burner1)
        if avg1> self.TEMPON:
            print ("UR burner on")
            stove.upper_right.burner_on = True
        avg2 = sum(burner2)/len(burner2)
        if avg2> self.TEMPON:
            print ("UL burner on")
            stove.upper_left.burner_on = True
        avg3 = sum(burner3)/len(burner3)
        if avg3> self.TEMPON:
            print ("LL burner on")
            stove.lower_left.burner_on = True
        avg4 = sum(burner4)/len(burner4)
        if avg4 > self.TEMPON:
            print("LR burner on")
            stove.lower_right.burner_on = True

        #get the temperature of each burner based on the maximum temperature
        UR_temp = max(burner1)
        UL_temp = max(burner2)
        LL_temp = max(burner3)
        LR_temp = max(burner4)

        stove.upper_right.temp = UR_temp
        stove.upper_left.temp = UL_temp
        stove.lower_left.temp = LL_temp
        stove.lower_right.temp = LR_temp
    
