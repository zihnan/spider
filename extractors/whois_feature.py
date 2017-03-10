import re
from extractor import Extractor
class Whois(Extractor):
    
    nothing = ['NOT FOUND',
            'No information',
            'No match for',
            'DOMAIN NOT FOUND',
            'no match',
            'This TLD has no whois server',
            'No entries found for the selected source(s)']
            
    invalid = ['Invalid domain name',
            'Invalid request']
            
    others = ['blacklisted',
            'Timeout',
            'Error for']
    
    def __init__(self, whois_str, **kwargs):
        self.whois = whois_str
        self.features = [self.is_with_whois]
    
    def get_none(self):
        return 0
    
    def __match(self, pattern, row):
        return re.match('^.*' + pattern.lower() + '.*$', row.rstrip().lower())
    
    def is_with_whois(self):
        for row in self.whois.split('\n'):
          if 'invalid' in row.rstrip().lower():
            for s in self.invalid:
              if self.__match(s, row):
                print 'invalid'
                print row
                return False
          elif 'no' in row.rstrip().lower():
            for s in self.nothing:
              if self.__match(s, row):
                print 'no'
                print row
                return False
          else:
            for s in self.others:
              if self.__match(s, row):
                print 'other'
                print row
                return False
        return True
