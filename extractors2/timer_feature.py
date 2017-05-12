
from extractor import Extractor
class timer(Extractor):
    def __init__(self, timer_str, **kwargs):
        self.time = float(timer_str)
        self.features = [self.get_time]
        
    def get_time(self):
        return self.time
        
