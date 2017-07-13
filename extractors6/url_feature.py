import alexa_req
import urllib
import re
import requests
from extractor import Extractor
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from xml.dom import minidom

from AWS_profile import AWSAccessKeyId
from AWS_profile import AWSSecretKey

awi = alexa_req.AlexaWebInfoRequest(AWSAccessKeyId,AWSSecretKey)

class URLExtractor(Extractor):
    def __init__(self, url):
        self.url = url
        self.keywords = self.get_keywords()
        self.features = [self.is_http_connection, self.is_ip_address, self.dots, self.is_special_words, self.url_linkin_num, self.url_traffic_rank]
        
    def is_special_words(self):
        return self.is_at_symbol() or self.is_dash_in_dir_struct() or self.is_start_in_dir_struct() or self.is_or_symbol_in_struct()
    
    def url_linkin_num(self):
        domain_name = self.get_domain_name(self.url)
        url_str = awi.get_alexa_url(domain_name)
        xml_str = urllib.urlopen(url_str).read()
        xmldoc = minidom.parseString(xml_str)
        obs_values = xmldoc.getElementsByTagName('aws:LinksInCount')
        try:
            linkin= obs_values[0].firstChild.nodeValue
            linkin = int(linkin)
            if linkin>10:
                return 1
        except:
            return 0
        return 0
    
    def url_traffic_rank(self):
        domain_name = self.get_domain_name(self.url)
        url_str = awi.get_alexa_url(domain_name)
        xml_str = urllib.urlopen(url_str).read()
        xmldoc = minidom.parseString(xml_str)
        obs_values = xmldoc.getElementsByTagName('aws:Rank')
        try:
            rank= obs_values[0].firstChild.nodeValue
            rank = int(rank)
            if rank<12000:
                return 2
            else:
                return 1
        except:
            return 0
        return 0
    
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
        
