from Adafruit_AMG88xx import Adafruit_AMG88xx
import Stove
import pygame
import os
import math
import time
import cv2
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

        self.points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
        self.grid_x, self.grid_y = np.mgrid[0:7:32j, 0:7:32j]

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def get_temperature(self, img_in, img_out, pixels_in):

        lst_intensities = []
        areas = []
        i = 0       
        avg = 0.0

        #blur image to help avoid smaller contours within burner
        blurred_in = cv2.GaussianBlur(img_in, (7, 7), 0)
        #give image rgb dimensions to turn it into grayscale
        im_in = np.stack((blurred_in,) * 3,-1)
        im_in = im_in.astype(np.uint8)
        bgr_in = cv2.cvtColor(im_in, cv2.COLOR_RGB2BGR)
        #turn image into grayscale
        gray_in = cv2.cvtColor(bgr_in, cv2.COLOR_BGR2GRAY)

		#blur image to help avoid smaller contours within burner
        blurred_out = cv2.GaussianBlur(img_out, (7, 7), 0)
        #give image rgb dimensions to turn it into grayscale
        im_out = np.stack((blurred_out,) * 3,-1)
        im_out = im_out.astype(np.uint8)
        bgr_out = cv2.cvtColor(im_out, cv2.COLOR_RGB2BGR)
        #turn image into grayscale
        gray_out = cv2.cvtColor(bgr_out, cv2.COLOR_BGR2GRAY)

	#find and draw contours
        ret, thresh = cv2.threshold(gray_in, 127, 255, 0)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	    
        cimg = np.zeros_like(gray_in)
        cv2.drawContours(cimg, contours, -1, color=255, thickness=-1)

	#check for the number of contours
        if len(contours) != 0:
        	#if there's more than one contour, set the index of the contour to be considered to that of the largest contour
            if len(contours)>1:
                for self.i in range(len(contours)):
                    area = cv2.contourArea(contours[i])
                    areas.append(area)
                    max_contour = areas.index(max(areas))
                    c = contours[max_contour]
            else:
                c = contours[0]
            #set contour index
            c_index = contours.index(c)  
            #get contour area  
            c_area = cv2.contourArea(c)
        else:
            c_index = None

	# Access the image pixels and create a 1D numpy array then add to list
        pts = np.where(cimg == 255)
        lst_intensities.append(img_out[pts[0], pts[1]])

        # map the color values back to temperature values
        if c_index != None:
            reverse_map = [self.map(p, min(lst_intensities[c_index]), max(lst_intensities[c_index]), min(pixels_in), max(pixels_in)) for p in lst_intensities[c_index]]
            if len(reverse_map) != 0:
            	#only consider contours of area larger than the minimum area
                if c_area > 20: 
                    avg = sum(reverse_map)/len(reverse_map)
                else:
                    avg = 0.0
        else:
            avg = 0.0
            
        return avg

    def update(self, stove):

        #read the pixels
        pixels = self.sensor.readPixels()

        #split the pixelview to 4 quarters representing each burner
        ary1 = pixels[:int(len(pixels)/2)]
        ary2 = pixels[int(len(pixels)/2):]
        pixels_ul = ary1[:int(len(ary1)/2)]
        pixels_ll = ary1[int(len(ary1)/2):]
        pixels_ur = ary2[:int(len(ary2)/2)]
        pixels_lr = ary2[int(len(ary2)/2):]

        pixels_out = [self.map(p, min(pixels), max(pixels), 0, 240) for p in pixels]
        bicubic_out = griddata(self.points, pixels_out, (self.grid_x, self.grid_y), method='cubic')

        #convert output image to numpy array
        out = np.array(bicubic_out)

        #set a temperature cap
        pixels_cap = [max(min(p, 80), 0) for p in pixels]

        #if maximum temperature is lower than the threshold, map maximum color to cap temperature
        if max(pixels_cap) < 30:
            pixels_in = [self.map(p, min(pixels_cap), 80, 0, 240) for p in pixels_cap]
        else:
            pixels_in = [self.map(p, min(pixels_cap), max(pixels_cap), 0, 240) for p in pixels_cap]

        bicubic_in = griddata(self.points, pixels_in, (self.grid_x, self.grid_y), method='cubic')

        #convert input image to numpy array
        img = np.array(bicubic_in)

        img.resize((32,32))

        #split input and output images to represent each burner and get their temperatures

        upper_left_in = img[0:16, 0:16]
        upper_left_out = out[0:16, 0:16]
        ul_temp = self.get_temperature(upper_left_in, upper_left_out, pixels_ul)
        stove.upper_left.temp = ul_temp

        lower_left_in = img[16:32, 0:16]
        lower_left_out = out[16:32, 0:16]
        ll_temp = self.get_temperature(lower_left_in, lower_left_out, pixels_ll)
        stove.lower_left.temp = ll_temp

        upper_right_in = img[0:16, 16:32]
        upper_right_out = out[0:16, 16:32]
        ur_temp = self.get_temperature(upper_right_in, upper_right_out, pixels_ur)
        stove.upper_right.temp = ur_temp

        lower_right_in = img[16:32, 16:32]
        lower_right_out = out[16:32, 16:32]
        lr_temp = self.get_temperature(lower_right_in, lower_right_out, pixels_lr)
        stove.lower_right.temp = lr_temp
