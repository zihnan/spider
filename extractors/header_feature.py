
from extractor import Extractor
class header(Extractor):
    def __init__(self, header_str, **kwargs):
        self.headers = {}
        if 'url' in kwargs:
          self.url = kwargs['url']
        for option in header_str.split('\n'):
            row = option.split(': ')
            if len(row) > 1:
                field, value = row[0], row[1]
                if field != 'Status':
                    self.headers[field] = value
            elif option.startswith('HTTP'):
                row = option.split(' ')
                self.headers['Status'] = row[1]
        self.redirect = self.get_redirect()
        self.features = [self.is_redirect]
    
    #8
    def get_redirect(self):
        try:
          k = (int(self.headers['Status']) / 100)
        except KeyError:
          print self.headers
          print self.url
        return (int(self.headers['Status']) / 100) == 3

    def is_redirect(self):
        return self.redirect

    def __add__(self, other):
        self.redirect = self.redirect or other.redirect
        return self
