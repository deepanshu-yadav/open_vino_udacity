import time
import numpy as np
class Inference:
    def __init__(self,model='abc'):
        self.model = model
    def perform_inference(self , image = None):
        interval = np.random.randint(6)
        time.sleep(interval/100)
        return interval