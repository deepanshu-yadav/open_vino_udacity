import time
import numpy as np
from network import Network
import cv2
class Inference:
    def __init__(self,model_file='model/tf_model.xml'):
        self.network = Network()
        self.network.load_model(model_file)
    def perform_inference(self , input_image = None):
        # interval = np.random.randint(6)
        # time.sleep(interval/100)
        # return interval
        input_details = self.network.get_input_shape()
        batch_size  , channels , height ,width = input_details[0] , input_details[1] , input_details[2] , input_details[3]
        image = self.preprocessing(input_image , height , width)
        self.network.async_inference(image)



    def preprocessing(self, input_image, height, width):
        '''
        Given an input image, height and width:
        - Resize to width and height
        - Transpose the final "channel" dimension to be first
        - Reshape the image to add a "batch" of 1 at the start
        '''
        image = np.copy(input_image)
        image = cv2.resize(image, (width, height))
        image = image.transpose((2,0,1))
        image = image.reshape(1, 3, height, width)

        return image

inf = Inference()

image = cv2.imread('test_image.jpg')
res = inf.perform_inference(image)
print(res)