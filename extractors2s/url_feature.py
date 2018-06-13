import re
import requests
import urllib
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from extractor import Extractor
from xml.dom import minidom
import alexa_req

AWSAccessKeyId='AKIAJWEULOS4W5J5ZFEQ'
AWSSecretKey='5CmDHmCDNChR1+tGg1iDIaOYXtWgowpgdSmedcXo'
awi = alexa_req.AlexaWebInfoRequest(AWSAccessKeyId,AWSSecretKey)
class URLExtractor(Extractor):
    def __init__(self, url):
        self.url = url
        self.keywords = self.get_keywords()
        self.features = [self.ip_or_hex, self.dots, self.is_at_symbol , self.url_length, self.url_linkin_num, self.url_traffic_rank]
        
    def is_special_words(self):
        return self.is_at_symbol() or self.is_dash_in_dir_struct() or self.is_start_in_dir_struct() or self.is_or_symbol_in_struct()
        
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
        
    #1 ip_address	//if has ip or hex =>1 else 0
    def ip_or_hex(self):
	if self.is_hexadecimal() or self.is_ip_address():
	    return 1
	return 0

    def is_ip_address(self):
        domain_name = self.get_domain_name(self.url)
        return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain_name) is not None
    
    
    def is_http_connection(self):
        return not self.url[:5] == 'https'
    
    #3 sub-domain	many phishing url subdomain<2?  
    def dots(self):
        domain_name = self.get_domain_name(self.url)
        part = len(domain_name.split('.')) -1
	if part <2:
	    res = 2
	elif part==2:
	    res = 1
	else:
	    res = 0
	return res
    
    #2 @ in the url	//if has @ => 1 else 0
    def is_at_symbol(self):
        quest_mark = self.url.find('?')
        if quest_mark > 0:
            url = self.url[:quest_mark]
        else:
            url = self.url
        return url.find('@') > -1
    
    
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





	#? number of url
	#0phishing   1legitimate
    def url_linkin_num(self):
	domain_name = self.get_domain_name(self.url)
	url_str = awi.get_alexa_url(domain_name)
	
	xml_str = urllib.urlopen(url_str).read()
	xmldoc = minidom.parseString(xml_str)

	obs_values = xmldoc.getElementsByTagName('aws:LinksInCount')
	# prints the first base:OBS_VALUE it finds
	try:
		linkin= obs_values[0].firstChild.nodeValue
		linkin = int(linkin)
		if linkin>10:
			return 1
	except:
		return 0
	return 0
    
    #5 website traffic
    # 0:phishy 1:suspicious 2:legitimate
    def url_traffic_rank(self):
	domain_name = self.get_domain_name(self.url)
        url_str = awi.get_alexa_url(domain_name)
	xml_str = urllib.urlopen(url_str).read()
	xmldoc = minidom.parseString(xml_str)

	obs_values = xmldoc.getElementsByTagName('aws:Rank')
	# prints the first base:OBS_VALUE it finds
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
    #4 length of url
    def url_length(self):	#short url??
        ulength = len(self.url)
        if ulength<54:
            res=2
        elif ulength>75:
            res=1
        else:
            res=0
        return res

        
