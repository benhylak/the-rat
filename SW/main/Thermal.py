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

class Thermal:

    def __init__(self):

        self.TEMPON = 45
        #low range of the sensor (this will be blue on the screen)
        self.MINTEMP = 18

        #high range of the sensor (this will be red on the screen)
        self.MAXTEMP = 100

        #how many color values we can have
        self.COLORDEPTH = 1024

        os.putenv('SDL_FBDEV', '/dev/fb1')
        pygame.init()

        #initialize the sensor
        self.sensor = Adafruit_AMG88xx()

        self.points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self.grid_x, self.grid_y = np.mgrid[0:7:32j, 0:7:32j]

        #sensor is an 8x8 grid so lets do a square
        self.height = 240
        self.width = 240

        #the list of colors we can choose from
        self.blue = Color("indigo")
        self.colors = list(self.blue.range_to(Color("red"), self.COLORDEPTH))

        #create the array of colors
        self.colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in self.colors]

        self.displayPixelWidth = self.width / 30
        self.displayPixelHeight = self.height / 30

        self.lcd = pygame.display.set_mode((self.width, self.height))

        self.lcd.fill((255,0,0))

        pygame.display.update()
        pygame.mouse.set_visible(False)

        self.lcd.fill((0,0,0))
        pygame.display.update()

    #some utility functions
    def constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    #let the sensor initialize
    #time.sleep(.1)
  
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
        
        pixels = [self.map(p, self.MINTEMP, self.MAXTEMP, 0, self.COLORDEPTH - 1) for p in pixels]

        #perdorm interpolation
        bicubic = griddata(self.points, pixels, (self.grid_x, self.grid_y), method='cubic')
        
        #draw everything
        for ix, row in enumerate(bicubic):
            for jx, pixel in enumerate(row):
                pygame.draw.rect(self.lcd, self.colors[self.constrain(int(pixel), 0, self.COLORDEPTH- 1)], (self.displayPixelHeight * ix, self.displayPixelWidth * jx, self.displayPixelHeight, self.displayPixelWidth))
                
        pygame.display.update()
