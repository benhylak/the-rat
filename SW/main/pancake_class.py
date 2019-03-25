from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry, Region
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient

import cv2
from PIL import Image
import numpy as np
import io

class PancakeClass:

    def __init__(self):
        self.ENDPOINT = "https://southcentralus.api.cognitive.microsoft.com"

        # Project keys
        self.training_key = "898c94f354ab4258b673466e46fd3f2b"
        self.prediction_key = "acf8ec355ca04bf2bd9c4f8b6701dce3"
        self.project_id = "3e3fc477-8439-423e-96b4-c19cbf7d4bb1"

        self.probability_min = 60

        # Now there is a trained endpoint that can be used to make a prediction

        self.predictor = CustomVisionPredictionClient(self.prediction_key, endpoint=self.ENDPOINT)

    def update(self, frame, stove):
        #split the image
        img = cv2.imread(frame)
        
        height, width = img.shape[:2]
        eighth_col = int(width / 8)
        center_col = int(width / 2)
        center_row = int(height / 2)

        first_quad = img[0:center_row, eighth_col:center_col]
        upper_left = "/home/pi/the-rat/SW/main/p1.jpg"
        cv2.imwrite(upper_left, first_quad)
        
        second_quad = img[0:center_row, center_col:width - eighth_col]
        upper_right = "/home/pi/the-rat/SW/main/p2.jpg"
        cv2.imwrite(upper_right, second_quad)
        
        third_quad = img[center_row:height, eighth_col:center_col]
        lower_left = "/home/pi/the-rat/SW/main/p3.jpg"
        cv2.imwrite(lower_left, third_quad)
        
        fourth_quad = img[center_row:height, center_col:width - eighth_col]
        lower_right = "/home/pi/the-rat/SW/main/p4.jpg"
        cv2.imwrite(lower_right, fourth_quad)

        self.detect(upper_left, stove.upper_left)
        self.detect(upper_right, stove.upper_right)
        self.detect(lower_left, stove.lower_left)
        self.detect(lower_right, stove.lower_right)

    def detect(self, frame, burner):
         # Open the sample image and get back the prediction results.
        with open(frame, mode="rb") as f:
            results = self.predictor.predict_image(self.project_id, f)
        for prediction in results.predictions:
            if (prediction.probability * 100 > self.probability_min):
                burner.recipe.status = prediction.tag_name

