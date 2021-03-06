import re
import requests
from extractor import Extractor
class URLExtractor(Extractor):
    def __init__(self, url):
        self.url = url
        self.keywords = self.get_keywords()
        self.features = [self.is_ip_address, self.dots, self.is_special_words, self.is_slashes]
        
    def is_slashes(self):
        p = self.url.find('//') + 2
        return self.url[p:].find('/') > 0
        
    def is_special_words(self):
        return self.is_at_symbol() or self.is_dash_in_dir_struct() or self.is_start_in_dir_struct() or self.is_or_symbol_in_struct()
        
    def is_long_url(self):
        return len(self.url) >= 127
        
    def get_keywords(self):
        temp = []
        shift = 0
        if self.is_ip_address():
            shift = len(self.get_domain_name(self.url))
            
        parameters = self.url[self.url.find('//') + 2 +shift:]

        if parameters.find('?') > -1:
            temp_parameters = parameters.split('?')
            parameters = temp_parameters[0]
            temp_parameters = temp_parameters[1:]
            
            for i in temp_parameters:
                if i.find("&") > -1:
                    temp += i.split('&')
        
        if parameters.find('/') > -1:
            for s in parameters.split('/'):
                if s.find('.') > -1:
                    temp += s.split('.')
                elif s.find('-') > -1:
                    temp += s.split('-')
                else:
                    temp.append(s)
                    
        temp_set = set(temp)
                
        return set([i for i in temp_set if not (i.startswith('htm') or i.startswith('php') or i == 'www')])
        
    #3
    def is_ip_address(self):
        domain_name = self.get_domain_name(self.url)
        return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain_name) is not None
    
    #4
    def is_http_connection(self):
        return not self.url[:5] == 'https'
    
    #2
    def dots(self):
        domain_name = self.get_domain_name(self.url)
        return len(domain_name.split('.')) -1
    
    #5
    def is_at_symbol(self):
        quest_mark = self.url.find('?')
        if quest_mark > 0:
            url = self.url[:quest_mark]
        else:
            url = self.url
        return url.find('@') > -1
    
    #6
    def is_hexadecimal(self):
        domain_name = self.get_domain_name(self.url)
        return domain_name.find('%') > -1
    
    def get_without_parameter(self):
        quest_mark = self.url.find('?')
        if quest_mark > 0:
            url = self.url[:quest_mark]
        else:
            url = self.url
        return url
    
    def is_or_symbol_in_struct(self):
        url = self.get_without_parameter()
        return url.find('|') > -1
    
    def is_dash_symbol(self):
        domain_name = self.get_domain_name(self.url)
        return domain_name.find('-') > -1
    
    def is_dash_in_dir_struct(self):
        url = self.get_without_parameter()
        return url.find('-') > -1
        
    def is_start_in_dir_struct(self):
        url = self.get_without_parameter()
        return url.find('*') > -1
        
