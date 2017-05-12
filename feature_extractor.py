import csv
import getopt
import inspect
import itertools
import lxml
import os
import re
import sys
from lxml import html
marks = ['HTTP', 'HEADER', 'WHOIS', 'HOST', 'NSLOOKUP', 'NSLOOKUPSUMMARY', 'NSLOOKUP', 'NSLOOKUPSUMMARY']

_current_module_path = os.path.dirname(__file__)
_extractors_fold_name = 'extractors'
sys.path.append(_current_module_path)
sys.path.append(os.path.join(_current_module_path, _extractors_fold_name))
from extractor import Extractor

def set_extractors_path(fold_name):
    global _extractors_fold_name
    _extractors_fold_name = fold_name
    sys.path[-1]=os.path.join(_current_module_path, _extractors_fold_name)
    
class FeatureExtractor:
    
    def __init__(self, data_list, **kwargs):
        self.verbose = False
        self.debug = False
        if 'verbose' in kwargs:
            self.verbose = kwargs['verbose']
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        if 'numeric' in kwargs:
            self.numeric = kwargs['numeric']
        else:
            self.numeric = False
        if 'quiet' in kwargs:
            self.quiet = kwargs['quiet']
        else:
            self.quiet = True
            
        self.init(data_list)
    
    def init(self, data_list):
        self.extractors = []
        if isinstance(data_list, list):
            self.data_list = data_list
        elif isinstance(data_list, str):
            self.data_list = data_list.split('\n')
        
        self.extractors = self.__get_extractors()
        self.extractors_features = {}
        self.data_block = {}
        self.__init_data_block()
        for i in self.data_block:
            self.extractors_features[i] = None
        
    def __init_data_block(self):
        for i in self.extractors:
            self.data_block[i] = []
            
    def add(self, extractor):
        self.extractors.append(extractor)
    
    def run(self):
        self.__split_data()
        features = []
        url = self.data_list[0]
        instance = self.extractors['url'](self.data_list[0]).set_verbose(self.verbose)
        instance.set_numeric(self.numeric)
        features += instance.extract()
        
        f2 = features
        for extractor_name in self.extractors:
            if extractor_name != 'url':
                temp = []
                pre = None
                if len(self.data_block[extractor_name]) > 0:
                    for data in self.data_block[extractor_name]:
                        instance = self.extractors[extractor_name](data, url=url)
                        instance.set_verbose(self.verbose)
                        instance.set_numeric(self.numeric)
                        instance.set_quiet(self.quiet)
                        if pre and isinstance(pre, self.extractors[extractor_name]):
                            instance += pre
                        pre = instance
                        temp = instance.extract()
                        self.extractors_features[extractor_name] = temp
                else:
                    if not self.quiet:
                        sys.stderr.write(extractor_name + ' Block: NOT CONTAINED IN DATA\n')
                    temp += [0] * len(self.extractors[extractor_name]('', url=url).features)
                f2 += temp
        if not self.quiet:
            sys.stderr.write(str(len(f2)) + '\n')
            sys.stderr.write(str(f2) + '\n')
        '''
        for block_name in self.data_block:
            if block_name != 'url':
                temp = []
                pre = None
                if len(self.data_block[block_name]) > 0:
                    for data in self.data_block[block_name]:
                        try:
                            instance = self.extractors[block_name](data, url=url)
                            instance.set_verbose(self.verbose)
                            instance.set_numeric(self.numeric)
                            instance.set_quiet(self.quiet)
                            if pre and isinstance(pre, self.extractors[block_name]):
                                instance += pre
                            pre = instance
                            temp = instance.extract()
                            self.extractors_features[block_name] = temp
                        except KeyError:
                            continue
                else:
                    temp = [0]
                    continue
                features += temp
        return features
        '''
        return f2
    
    def __split_data(self): 
        entries = 0
        temp_block = ''
        
        for l in self.data_list:
            if re.match('^<=.* BEGIN=>$', l.strip()):
                entries += 1
                class_type = l.split()
                if class_type[0][2:] != 'NSLOOKUPSUMMARY':
                    class_type = class_type[0][2:]
            elif re.match('^<=.* END=>$', l.strip()):
                if class_type != 'NSLOOKUPSUMMARY' and entries == 1:
                    try:
                        self.data_block[class_type.lower()].append(temp_block)
                    except KeyError:
                        self.data_block[class_type.lower()] = [temp_block]
                    temp_block = ''
                    entries -= 1
            elif entries > 0:
                temp_block += l
    
    def __get_extractors(self):
        extractor_list = {}
        for extractor_module in os.listdir(os.path.join(_current_module_path, _extractors_fold_name)):
            if extractor_module.endswith("feature.py"):
                module = __import__(extractor_module[:-3])
                for attr in dir(module):
                    subclass = getattr(module, attr)
                    if inspect.isclass(subclass) and issubclass(subclass, Extractor):
                        extractor_list[extractor_module[:extractor_module.find('_')]] = subclass
        return extractor_list
        
def help_message():
    print '''
    spider [-h]
    spider [-d OUTPUT_DIR][-i INPUTFILE]
    spider [-d OUTPUT_DIR][-u HTTP_URL]
'''
    
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
    features = {'url_length':-1,'dots':-1,'is_ip_address':False,'is_ssl_connection':False,'is_at_symbol':False,'is_hexadecimal':False,'is_frame':False,'is_redirect':False,'is_submit':False}
    print [i for i in features]
    print '=> Done <='

def ext(input_file, verbose=None, outputfile=None, outputdir=None):
    temp = ''
    entries = 0
    features = {'url_length':-1,'dots':-1,'is_ip_address':False,'is_ssl_connection':False,'is_at_symbol':False,'is_hexadecimal':False,'is_frame':False,'is_redirect':False,'is_submit':False}
    
    with open(input_file, 'r') as f:
        url = f.readline()
        features['url_length'] = len(url)
        feature_fields = ['is_ip_address','is_ssl_connection','dots','is_at_symbol','is_hexadecimal']
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
                    module = __import__(__file__[:-2])
                    _class = getattr(module, class_name)
                    instance = _class(url, temp, outputfile)
                    if class_name == 'http':
                        features['is_frame'] = features['is_frame'] or instance.is_frame()
                        features['is_redirect'] = features['is_redirect'] or instance.is_redirect()
                        features['is_submit'] = features['is_submit'] or instance.is_submit()
                    elif class_name == 'header':
                        features['is_redirect'] = features['is_redirect'] or instance.is_redirect()
                    elif class_name == 'host':
                        instance.ipv4_numbers()
                        instance.ipv6_numbers()
                    temp = ''
            else:
                temp += l
                
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

def get_long(fields):
    field_list = []
    for field in fields:
        if len(field) == 2:
            field_list.append(field[1][2:])
        else:
            if field[0].startswith('--'):
                field_list.append(field[0][2:])
    return field_list

def get_short(fields):
    field_list = []
    for field in fields:
        if len(field) == 2:
            if field[1][-1] == '=':
                field_list.append(field[0][1] + ':')
            else:
                field_list.append(field[0][1])
        else:
            if field[0].startswith('--'):continue
            else:
                field_list.append(field[0][1])
    return field_list

def main(argv):
    input_file = None
    verbose = False
    debug = False
    numeric = False
    quiet = False
    url = None
    redirect_cycle_times = 2
    output_dir = None
    output_file = None
    input_dir = None
    field_pairs = (('-v',), ('-h','--help'), ('-i', '--inputfile='), ('-d', '--outputdir='), ('-o','--outputfile='), ('--startwith=',), ('--input-dir=',),('--debug',), ('-n','--numeric'), ('--quiet',), ('--select=',))
    
    try:
        opts,args = getopt.getopt(argv, ''.join(get_short(field_pairs)), get_long(field_pairs))
        for opt,arg in opts:
            if opt in ('-v'):
                verbose = True
            elif opt in ('--debug'):
                debug = True
            elif opt in ('-h','--help'):
                help_message()
            elif opt in ('-i', '--inputfile='):
                input_file = str(arg)
            elif opt in ('-d', '--outputdir='):
                output_dir = arg
            elif opt in ('-o','--outputfile='):
                output_file = str(arg)
            elif opt in ('--startwith=',):
                start_number = int(arg)
            elif opt in ('--input-dir=',):
                input_dir = str(arg)
            elif opt in ('-n','--numeric'):
                numeric = True
            elif opt in field_pairs[-1]:
                quiet = True
            elif opt in '--select=':
                sys.stderr.write('Set Extractor Path: {}\n'.format(str(arg)))
                set_extractors_path(str(arg))
        
        if len(args) > 0:
            for arg in args:
                with open(arg, 'r') as f:
                    block = f.readlines()
                temp = FeatureExtractor(block, verbose=verbose, debug=debug, numeric=numeric, quiet=quiet).run()
                if verbose:
                  print 'length: ',len(temp)
                print temp
    except getopt.GetoptError as err:
        print str(err)
        help_message()

if __name__ == '__main__':
    main(sys.argv[1:])
