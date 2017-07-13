
from extractor import Extractor
class cycling(Extractor):
    def __init__(self, cycling_str, **kwargs):
        self.cycling = cycling_str
        self.features = [self.is_cycling]
        
    def is_cycling(self):
        return len(set(self.cycling.split('\n')))
