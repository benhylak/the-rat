from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry, Region
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient

class PotDetector:

    def __init__(self):
        self.ENDPOINT = "https://southcentralus.api.cognitive.microsoft.com"

        # Project keys
        self.training_key = "dae03cb013f840658708cd62781d90c1"
        self.prediction_key = "6212b24516c6492190c63d2b32084079"
        self.project_id = "a97fb679-77e7-4e07-b946-81c752ee3112"

        self.probability_min = 60

        # Now there is a trained endpoint that can be used to make a prediction

        self.predictor = CustomVisionPredictionClient(self.prediction_key, endpoint=self.ENDPOINT)

    def update(self, frame, stove):
        # Open the sample image and get back the prediction results.
        results = self.predictor.predict_image(self.project_id, frame)
        
        center_x = 0.0
        center_y = 0.0

        stove.upper_right.pot_detected = False
        stove.upper_left.pot_detected = False
        stove.lower_left.pot_detected = False
        stove.lower_right.pot_detected = False

        # Display the results.
        for prediction in results.predictions:
                
            if (prediction.probability * 100 > self.probability_min):
                center_x = prediction.bounding_box.left + ((prediction.bounding_box.width)/2)
                center_y = prediction.bounding_box.top + ((prediction.bounding_box.height)/2)

                if (center_x > 0.5 and center_y < 0.5):
                    stove.upper_right.pot_detected = True
                elif (center_x < 0.5 and center_y < 0.5):
                    stove.upper_left.pot_detected = True
                elif (center_x < 0.5 and center_y > 0.5):
                    stove.lower_left.pot_detected = True
                elif (center_x > 0.5 and center_y > 0.5):
                    stove.lower_right.pot_detected = True