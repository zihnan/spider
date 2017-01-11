import csv
import getopt
import os
import re
import sys
from lxml import html
marks = ['HTTP', 'HEADER', 'WHOIS', 'HOST', 'NSLOOKUP', 'NSLOOKUPSUMMARY', 'NSLOOKUP', 'NSLOOKUPSUMMARY']

def help_message():
    print '''
    spider [-h]
    spider [-d OUTPUT_DIR][-i INPUTFILE]
    spider [-d OUTPUT_DIR][-u HTTP_URL]
'''

class header:
    def __init__(self, header_str, outputfile):
        print 'header'

class whois:
    def __init__(self, header_str, outputfile):
        print "whois"

class nslookup:
    def __init__(self, header_str, outputfile):
        print "nslookup"

class nslookupsummary:
    def __init__(self, header_str, outputfile):
        print "nslookupsummary"
        
class host:
    def __init__(self, header_str, outputfile):
        print "host"
        
class Extractor:
    def run(self):
        pass

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
    
    def __init__(self, html_str, outputfile):
        print 'http'
        try:
            self.html_tree = html.fromstring(html_str)
        except Exception as e:
            print 'EEEEE'

        self.outputfile = outputfile
        self.url

    def is_frame(self):
        print 'Heate'
        print self.html_tree.Xpath('//iframe')
        return self.html_tree.Xpath('//iframe') is not None

def is_ip_address(url):
    domain_name = get_domain_name(url)
    return re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain_name) is not None

def is_ssl_connection(url):
    return url[:5] == 'https'

def dots(url):
    domain_name = get_domain_name(url)
    return len(domain_name.split('.') - 1)

def is_at_symbol(url):
    domain_name = get_domain_name(url)
    return domain_name.find('@') > -1

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
        if current + '/' + i:
            ext(input_file, verbose=verbose, outputfile=outputfile, outputdir=outputdir,)

def ext(input_file, verbose=None, outputfile=None, outputdir=None):
    temp = ''
    with open(input_file, 'r') as f:
        for l in f.readlines():
            if re.match('^<=.* BEGIN=>$', l.strip()):
                class_type = l.split()
                if class_type[0][2:] != 'NSLOOKUPSUMMARY':
                    class_type = class_type[0][2:]
            elif re.match('^<=.* END=>$', l.strip()):
                if class_type != 'NSLOOKUPSUMMARY':
                    class_name = class_type.lower()
                    print "class name:",class_name
                    module = __import__(__file__[:-2])
                    _class = getattr(module, class_name)
                    instance = _class(temp, outputfile)
                    if class_name.startswith( 'http'):
                        print 'xxx'
                        if instance.is_frame():
                            print 1
                        elif instance.is_frame() == False:
                            print 0
                    temp = ''
            else:
                temp += l

def main(argv):
    input_file = None
    verbose = False
    url = None
    redirect_cycle_times = 2
    output_dir = None
    output_file = None
    input_dir = None
    try:
        opts,args = getopt.getopt(argv, 'hi:vd:f:', ['help',' inputfile=', 'outputdir=', 'startwith=', 'outputfile=', 'input-dir='])
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
                
        #error_log = open('error.log','a')
        if input_dir is not None:
            extract_from_dir(input_dir, outputfile=output_file, outputdir=output_dir, verbose=verbose)
        elif input_file is not None:
            ext(input_file, verbose=verbose, outputfile=output_file, outputdir=output_dir)
    except getopt.GetoptError as err:
        print str(err)
        help_message()
    finally:
        #error_log.close()
        sys.exit(2)

if __name__ == '__main__':
  main(sys.argv[1:])
