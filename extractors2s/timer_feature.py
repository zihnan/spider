
from extractor import Extractor
class timer(Extractor):
    def __init__(self, timer_str, **kwargs):
        self.time = float(timer_str)
        self.features = []
        
    def get_time(self):
        return self.time
        
