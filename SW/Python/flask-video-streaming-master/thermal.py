from Adafruit_AMG88xx import Adafruit_AMG88xx
import pygame
import os
import math
import time
from time import sleep

import numpy as np
from scipy.interpolate import griddata

from colour import Color

TEMPON = 45
#low range of the sensor (this will be blue on the screen)
MINTEMP = 18

#high range of the sensor (this will be red on the screen)
MAXTEMP = 100

#how many color values we can have
COLORDEPTH = 1024

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()

#initialize the sensor
sensor = Adafruit_AMG88xx()

points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

#sensor is an 8x8 grid so lets do a square
height = 240
width = 240

#the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

#create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30

lcd = pygame.display.set_mode((width, height))

lcd.fill((255,0,0))

pygame.display.update()
pygame.mouse.set_visible(False)

lcd.fill((0,0,0))
pygame.display.update()

#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

#let the sensor initialize
time.sleep(.1)
    
while(1):

    #read the pixels
    pixels = sensor.readPixels()

    #split the display into 4 parts to represent each burner
    ary1 = pixels[:len(pixels)/2]
    ary2 = pixels[len(pixels)/2:]
    burner1 = ary1[:len(ary1)/2]
    burner2 = ary1[len(ary1)/2:]
    burner3 = ary2[:len(ary2)/2]
    burner4 = ary2[len(ary2)/2:]

    #detect if a burner is on based on the average temperature
    avg1 = sum(burner1)/len(burner1)
    if avg1> TEMPON:
        print ("UR burner on")
    avg2 = sum(burner2)/len(burner2)
    if avg2> TEMPON:
        print ("UL burner on")
    avg3 = sum(burner3)/len(burner3)
    if avg3> TEMPON:
        print ("LL burner on")
    avg4 = sum(burner4)/len(burner4)
    if avg4 >TEMPON:
        print("LR burner on")

    #get the temperature of each burner based on the maximum temperature
    UR_temp = max(burner1)
    UL_temp = max(burner2)
    LL_temp = max(burner3)
    LR_temp = max(burner4)
    
    pixels = [map(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
    
    #perdorm interpolation
    bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
    
    #draw everything
    for ix, row in enumerate(bicubic):
        for jx, pixel in enumerate(row):
            pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH- 1)], (displayPixelHeight * ix, displayPixelWidth * jx, displayPixelHeight, displayPixelWidth))
            
    pygame.display.update()
    pygame.image.save(lcd, "1.jpg")
    pygame.display.update()
    pygame.image.save(lcd, "2.jpg")
    pygame.display.update()
    pygame.image.save(lcd, "3.jpg")
