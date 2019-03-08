from Adafruit_AMG88xx import Adafruit_AMG88xx
import Stove
import pygame
import os
import math
import time
import cv2
from time import sleep
from moving_average import MovingAverage

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
        
        #height and width of processed image
        self.height = 32
        self.width = 32
        
        #minimum contour area
        self.min_area = 20
        
        #minimum temperature 
        self.min_temp = 30
        
        #cap on maximum temperature for input picture
        self.temp_cap = 80
        
        #maximum color mapping
        self.max_color = 240
        
        self.max_samples = 20 #the number of samples in the temperature average array
        self.moving_average_ur = MovingAverage(self.max_samples)
        self.moving_average_ul = MovingAverage(self.max_samples)
        self.moving_average_ll = MovingAverage(self.max_samples)
        self.moving_average_lr = MovingAverage(self.max_samples)

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max):
      return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def get_temperature(self, img_in, img_out, pixels_in, moving_average):

        lst_intensities = []
        areas = []
        i = 0       
        avg = 0.0

        #turn input image into grayscale
        blurred_in = cv2.GaussianBlur(img_in, (7, 7), 0) #blur to avoid smaller contours inside burner contours
        im_in = np.stack((blurred_in,) * 3,-1)
        im_in = im_in.astype(np.uint8)
        bgr_in = cv2.cvtColor(im_in, cv2.COLOR_RGB2BGR)
        gray_in = cv2.cvtColor(bgr_in, cv2.COLOR_BGR2GRAY)

	#turn output image into grayscale
        im_out = np.stack((img_out,) * 3,-1)
        im_out = im_out.astype(np.uint8)
        bgr_out = cv2.cvtColor(im_out, cv2.COLOR_RGB2BGR)
        gray_out = cv2.cvtColor(bgr_out, cv2.COLOR_BGR2GRAY)

	#find and draw contours
        ret, thresh = cv2.threshold(gray_in, 127, 255, 0)
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        #mask the chosen contour and draw it on the input image
        cimg = np.zeros_like(gray_in)
        cv2.drawContours(cimg, contours, -1, color=255, thickness=-1)

	#check for the number of contours
        if len(contours) != 0:
            #if there's more than one contour, only keep the largest one
            if len(contours)>1:
                for i in range(len(contours)):
                    area = cv2.contourArea(contours[i])
                    areas.append(area)
                    max_contour = areas.index(max(areas))
                    c = contours[max_contour]
            else:
                c = contours[0]
            
            c_index = contours.index(c)    
            c_area = cv2.contourArea(c)
        else:
            c_index = None

	# Access the image pixels and create a 1D numpy array then add to list
        pts = np.where(cimg == 255)
        # add the pixels covered by the mask in the output image to a list
        lst_intensities.append(img_out[pts[0], pts[1]])

        #only record temperature if a contour was found, otherwise set temperature to zero
        if c_index != None:
            # map the color values back to temperature values
            reverse_map = [self.map(p, min(lst_intensities[c_index]), max(lst_intensities[c_index]), min(pixels_in), max(pixels_in)) for p in lst_intensities[c_index]]
            if len(reverse_map) != 0:
                if c_area > self.min_area:
                    temp = sum(reverse_map)/len(reverse_map)
                    #use the moving average array passed in to get the average of temperature over time
                    temp_avg = moving_average.process(temp)
                    #calculate the average of averages in the moving array
                    avg = sum(temp_avg)/len(temp_avg)
                                                        
                else:
                    avg = 0.0
        else:
            avg = 0.0
        
        return avg

    def update(self, stove):

        #read the pixels
        pixels = self.sensor.readPixels()

        #split the pixelview to 4 quarters to be used for mapping color values back to temperature values
        ary1 = pixels[:int(len(pixels)/2)]
        ary2 = pixels[int(len(pixels)/2):]
        pixels_ul = ary1[:int(len(ary1)/2)]
        pixels_ll = ary1[int(len(ary1)/2):]
        pixels_ur = ary2[:int(len(ary2)/2)]
        pixels_lr = ary2[int(len(ary2)/2):]
        
        #map the output image to pixel values with no temperature cap
        pixels_out = [self.map(p, min(pixels), max(pixels), 0, self.max_color) for p in pixels]
        bicubic_out = griddata(self.points, pixels_out, (self.grid_x, self.grid_y), method='cubic')

        #output picture has the pixel values mapped correctly
        out = np.array(bicubic_out)
        
        #set the maximum temperature to the temperature cap
        pixels_cap = [max(min(p, self.temp_cap), 0) for p in pixels]

        #if the maximum temperature is low, map the maximum color to the temperature cap
        if max(pixels_cap) < self.min_temp:
            pixels_in = [self.map(p, min(pixels_cap), self.temp_cap, 0, self.max_color) for p in pixels_cap]
        else:
            pixels_in = [self.map(p, min(pixels_cap), max(pixels_cap), 0, self.max_color) for p in pixels_cap]

        bicubic_in = griddata(self.points, pixels_in, (self.grid_x, self.grid_y), method='cubic')

        #input image has a cap on the maximum temperature
        img = np.array(bicubic_in)

        img.resize((self.height,self.width))

        #split input and output images to represent each burner and get their temperatures

        upper_left_in = img[0:int((self.width/2)), 0:int((self.height/2))]
        upper_left_out = out[0:int((self.width/2)), 0:int((self.height/2))]
        stove.upper_left.temp = self.get_temperature(upper_left_in, upper_left_out, pixels_ul, self.moving_average_ul)

        lower_left_in = img[int((self.width/2)):self.width, 0:int((self.height/2))]
        lower_left_out = out[int((self.width/2)):self.width, 0:int((self.height/2))]
        stove.lower_left.temp = self.get_temperature(lower_left_in, lower_left_out, pixels_ll, self.moving_average_ll)
        
        upper_right_in = img[0:int((self.width/2)), int((self.height/2)):self.height]
        upper_right_out = out[0:int((self.width/2)), int((self.height/2)):self.height]
        stove.upper_right.temp = self.get_temperature(upper_right_in, upper_right_out, pixels_ur, self.moving_average_ur)

        lower_right_in = img[int((self.width/2)):self.width, int((self.height/2)):self.height]
        lower_right_out = out[int((self.width/2)):self.width, int((self.height/2)):self.height]
        stove.lower_right.temp = self.get_temperature(lower_right_in, lower_right_out, pixels_lr, self.moving_average_lr)
