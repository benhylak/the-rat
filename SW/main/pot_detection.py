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

        # Now there is a trained endpoint that can be used to make a prediction

        self.predictor = CustomVisionPredictionClient(self.prediction_key, endpoint=self.ENDPOINT)

    def update(self,image_path, stove):
        # Open the sample image and get back the prediction results.
        with open(image_path, mode="rb") as test_data:
            results = self.predictor.predict_image(self.project_id, test_data)
        
        left_center = 0.0
        top_center = 0.0

        # Display the results.
        for prediction in results.predictions:
                
            if (prediction.probability * 100 > 80):
                left_center = prediction.bounding_box.left + ((prediction.bounding_box.width)/2)
                top_center = prediction.bounding_box.top + ((prediction.bounding_box.height)/2)

                if (left_center > 0.5 and top_center < 0.5):
                    stove.upper_right.on = True
                elif (left_center < 0.5 and top_center < 0.5):
                    stove.upper_left.on = True
                elif (left_center < 0.5 and top_center > 0.5):
                    stove.lower_left.on = True
                elif (left_center > 0.5 and top_center > 0.5):
                    stove.lower_right.on = True