import sys
from extractor import Extractor
class header(Extractor):
    def __init__(self, header_str, **kwargs):
        self.headers = {}
        if 'url' in kwargs:
          self.url = kwargs['url']
        
        temp_field = None
        
        header_list = header_str.rstrip().split('\n')
        row = header_list[0].split(' ')
        self.headers['Status'] = row[1]
        for option in header_list[1:]:
            if option.find(': ') > -1:
                row = option.split(': ')
                field, value = row[0], row[1]
                temp_field = field
                if field != 'Status':
                    self.headers[field] = value
            else:
                self.headers[temp_field] += option.strip().rstrip()
            '''
            if option.startswith('HTTP/'):
                row = option.split(' ')
                self.headers['Status'] = row[1]
            else:
                row = option.split(': ')
                field, value = row[0], row[1]
                if field != 'Status':
                    self.headers[field] = value
            '''
        
        self.redirect = self.get_redirect()
        self.features = []
        
    
    
    #8
    def get_redirect(self):
        try:
          k = (int(self.headers['Status']) / 100)
        except KeyError:
          sys.stderr.write(self.headers)
          sys.stderr.write(self.url)
        return (int(self.headers['Status']) / 100) == 3

    def is_redirect(self):
        return self.redirect

    def __add__(self, other):
        self.redirect = self.redirect or other.redirect
        return self
