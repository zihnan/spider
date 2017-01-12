import csv
import getopt
import inspect
import lxml
import os
import re
import sys
from lxml import html
marks = ['HTTP', 'HEADER', 'WHOIS', 'HOST', 'NSLOOKUP', 'NSLOOKUPSUMMARY', 'NSLOOKUP', 'NSLOOKUPSUMMARY']

sys.path.append(os.getcwd())

class FeatureExtractor:
    def __init__(self, dir_name=None):
        self.init(dir_name)
    
    def init(self, dir_name):
        if dir_name:
            self.dir_name = dir_name
        else:
            self.dir_name = 'extractor'
        self.extractors = self.get_extractors()
        print self.extractors

    def run(self):
        features = []
        for extractor in self.extractors:
            func = getattr(extractor, 'extract')
            func()
            #features.append(func())
        return features
    
    def get_extractors(self):
        extractor_list = []
        sys.path.append(self.dir_name)
        for extractor_module in os.listdir(self.dir_name):
            if extractor_module.endswith("feature.py"):
                module = __import__(extractor_module[:-3])
                for attr in dir(module):
                    subclass = getattr(module, attr)
                    if inspect.isclass(subclass) and issubclass(subclass, Extractor):
                        extractor_list.append(subclass())
        return extractor_list
                        
    def get_redirect(self):
        print "get_redirect"
        
    def get_post(self):
        print "get_post"
        
class Extractor:
    def extract(self):
        pass

def help_message():
    print '''
    spider [-h]
    spider [-d OUTPUT_DIR][-i INPUTFILE]
    spider [-d OUTPUT_DIR][-u HTTP_URL]
'''

class timer:
    def __init__(self, url, timer_str,outputfile):
        self.url = url

class header:
    def __init__(self, url, header_str, outputfile):
        print 'header'
        self.headers = {}
        self.url = url
        for option in header_str.split('\n'):
            row = option.split(': ')
            if len(row) > 1:
                field, value = row[0], row[1]
                self.headers[field] = value
            elif option.startswith('HTTP'):
                row = option.split(' ')
                self.headers['Status'] = row[1]
    
    #8
    def is_redirect(self):
        return (int(self.headers['Status']) / 100) == 3

class cycling:
    def __init__(self, url, cycling_str, outpurfile):
        print "cycling"
        self.url = url

class whois:
    def __init__(self, url, header_str, outputfile):
        print "whois"
        self.url = url

class nslookup:
    def __init__(self, url, header_str, outputfile):
        print "nslookup"
        self.url = url

class nslookupsummary:
    def __init__(self, url, header_str, outputfile):
        print "nslookupsummary"
        self.url = url
        
class host:
    def __init__(self, url, host_str, outputfile):
        print "host"
        self.ipv4_address_list = []
        self.ipv6_address_list = []
        self.url = url

        for row in host_str.split('\n'):
            if row:
                cols = row.split(' ')
                if cols[2] == 'address':
                    self.ipv4_address_list.append(cols[3])
                elif cols[2] == 'IPv6':
                    self.ipv6_address_list.append(cols[4])

    def ipv4_numbers(self):
        return len(self.ipv4_address_list)

    def ipv6_numbers(self):
        return len(self.ipv6_address_list)
        
class http:
    url_length = None
    dots = None
    ip_address = None
    ssl_connetction = None
    at_symbol = None
    hexadecimal = None
    frame = None
    redirect = None
    submit = None
    
    def __init__(self, url, html_str, outputfile):
        print 'http'
        self.html_tree = html.fromstring(html_str)
        self.url = url
        self.outputfile = outputfile

    def get_frame(self):
        return self.html_tree.xpath('//iframe')

    #7
    def is_frame(self):
        if self.get_frame():
            return True
        return False

    def get_redirect(self):
        return self.html_tree.xpath('//meta[@http-equiv="refresh"]')

    #8
    def is_redirect(self):
        if self.get_redirect():
            return True
        return False

    def get_submit(self):
        return self.html_tree.xpath('//*[@type="submit"]')

    #9
    def is_submit(self):
        if self.get_submit():
            return True
        return False

#3
def is_ip_address(url):
    domain_name = get_domain_name(url)
    return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain_name) is not None

#4
def is_ssl_connection(url):
    return url[:5] == 'https'

#2
def dots(url):
    domain_name = get_domain_name(url)
    return len(domain_name.split('.')) -1

#5
def is_at_symbol(url):
    domain_name = get_domain_name(url)
    return domain_name.find('@') > -1

#6
def is_hexadecimal(url):
    domain_name = get_domain_name(url)
    return domain_name.find('%') > -1
    
def get_domain_name(url):
        domain_name = url[url.find('//')+2:]
        escape = domain_name.find('/')
        if domain_name.find('/') > 0:
            domain_name = domain_name[:escape]
        else:
            if domain_name.find('?') > 0:
                domain_name = domain_name[:domain_name.find('?')]
        commas = domain_name.rfind(':')
        if commas > 0:
            domain_name = domain_name[:commas]
        return domain_name
    
def extract_from_dir(input_dir, verbose=None, outputfile=None, outputdir=None):
    current = os.getcwd()
    for i in os.listdir(input_dir):
        ext(input_dir + '/' + i, verbose=verbose, outputfile=outputfile, outputdir=outputdir)

def ext(input_file, verbose=None, outputfile=None, outputdir=None):
    temp = ''
    entries = 0
    features = {'url_length':-1,'dots':-1,'is_ip_address':False,'is_ssl_connection':False,'is_at_symbol':False,'is_hexadecimal':False,'is_frame':False,'is_redirect':False,'is_submit':False}
    
    with open(input_file, 'r') as f:
        url = f.readline()
        features['url_length'] = len(url)
        feature_fields = ['is_ip_address','is_ssl_connection','dots','is_at_symbol','is_hexadecimal']
        redirect=False
        module = __import__(__file__[:-2])
        for i in feature_fields:
            _method = getattr(module, i)
            features[i] = _method(url)
        
        for l in f.readlines():
            if re.match('^<=.* BEGIN=>$', l.strip()):
                entries += 1
                class_type = l.split()
                if class_type[0][2:] != 'NSLOOKUPSUMMARY':
                    class_type = class_type[0][2:]
            elif re.match('^<=.* END=>$', l.strip()):
                if class_type != 'NSLOOKUPSUMMARY':
                    class_name = class_type.lower()
                    print "class name:",class_name
                    module = __import__(__file__[:-2])
                    _class = getattr(module, class_name)
                    try:
                        instance = _class(url, temp, outputfile)
                    except lxml.etree.ParserError:
                        print input_file
                    print '\t',
                    if class_name == 'http':
                        features['is_frame'] = features['is_frame'] or instance.is_frame()
                        features['is_redirect'] = features['is_redirect'] or instance.is_redirect()
                        features['is_submit'] = features['is_submit'] or instance.is_submit()
                    elif class_name == 'header':
                        features['is_redirect'] = features['is_redirect'] or instance.is_redirect()
                        if features['is_redirect']:
                            redirect = True
                    elif class_name == 'host':
                        print "ipv4:",instance.ipv4_numbers()
                        print '\t',
                        print "ipv6:",instance.ipv6_numbers()
                    temp = ''
            else:
                temp += l
    print
    temp_feature = []
    for i in features:
        print i,
        if type(features[i]) is bool:
            if features[i]:
                temp_feature.append(1)
            else:
                temp_feature.append(0)
        else:
            temp_feature.append(features[i])
    print
        
    with open('csv.test', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(temp_feature)

def main(argv):
    input_file = None
    verbose = False
    url = None
    redirect_cycle_times = 2
    output_dir = None
    output_file = None
    input_dir = None
    try:
        opts,args = getopt.getopt(argv, 'hi:vd:f:t', ['help',' inputfile=', 'outputdir=', 'startwith=', 'outputfile=', 'input-dir='])
        for opt,arg in opts:
            if opt in ('-v'):
                verbose = True
            elif opt in ('-h','--help'):
                help_message()
            elif opt in ('-i', '--inputfile='):
                input_file = str(arg)
            elif opt in ('-d', '--outputdir='):
                output_dir = arg
            elif opt in ('-o','--outputfile='):
                output_file = str(arg)
            elif opt in ('--startwith='):
                start_number = int(arg)
            elif opt in ('--input-dir='):
                input_dir = str(arg)
            elif opt in ('-t'):
                FeatureExtractor().run()
                return
                
        #error_log = open('error.log','a')
        if input_dir is not None:
            extract_from_dir(input_dir, outputfile=output_file, outputdir=output_dir, verbose=verbose)
        elif input_file is not None:
            ext(input_file, verbose=verbose, outputfile=output_file, outputdir=output_dir)
    except getopt.GetoptError as err:
        print str(err)
        help_message()

if __name__ == '__main__':
    main(sys.argv[1:])
