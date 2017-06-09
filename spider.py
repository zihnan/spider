# coding=UTF-8
import codecs
import commands
import dns.resolver
import ftplib
import getopt
import re
import requests
import sys
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from functools import wraps
from lxml import html
from lxml import etree
from lxml.etree import *
from requests.exceptions import *

def time_logger(log_file):
    def timer(func):
        @wraps(func)
        def time_wrap(*arg, **kwargs):
            pre_time = time.time()
            o = func(*arg, **kwargs)
            total_time = time.time() - pre_time
            if isinstance(log_file, file):
                log_file.write("\n<=TIMER BEGIN=>\n")
                log_file.write(str(total_time) + '\n') 
                log_file.write("\n<=TIMER END=>\n")
        return time_wrap
    return timer

class DownloadFile:
    verbose = False
    
    def run(self):
        pass

    def get_timer(self, use_time):
        s = "\n<=TIMER BEGIN=>\n"
        s += str(use_time) + '\n'
        s += "\n<=TIMER END=>\n"
        return s
        
    def get_domain_name(self, url):
        domain_name = url[url.find('//')+2:]
        escape = domain_name.find('/')
        if escape > -1:
            domain_name = domain_name[:escape]
        else:
            if domain_name.find('?') > -1:
                domain_name = domain_name[:domain_name.find('?')]
        at_symbol = domain_name.find('@')
        if at_symbol > -1:
            domain_name = domain_name[at_symbol+1:]
        commas = domain_name.rfind(':')
        if commas > -1:
            domain_name = domain_name[:commas]
        print domain_name
        return domain_name

    def get_nslookup(self, domain_name):
        count = 0
        s = '\n<=NSLOOKUP BEGIN=>\n'
        status = commands.getstatusoutput('nslookup -type=soa %s' % domain_name)
        s += status[1]
        s += '\n'
        status = commands.getstatusoutput('nslookup %s' % domain_name)
        s += status[1]
        s += '\n<=NSLOOKUP END=>\n'
        return get_utf8(s)

    def get_host(self, domain_name):
        s = '\n<=HOST BEGIN=>\n'
        status = commands.getstatusoutput('host %s' % domain_name)
        s += status[1]
        s += '\n<=HOST END=>\n'
        return get_utf8(s)

    def get_whois(self, domain_name):
        s = '\n<=WHOIS BEGIN=>\n'
        status = commands.getstatusoutput('whois %s' % domain_name)
        temp = status[1]
        for index,row in enumerate(temp):
            try:
                s += row
            except:
                print index
                print row
                s += row.decode('utf-8', errors='replace')
        s += '\n<=WHOIS END=>\n'
        #return get_utf8(s)
        return s.decode('utf-8')

    def logger(self, msg):
        if self.verbose:
            try:
                sys.stderr.write(str(msg) + '\n')
            except Exception as e:
                print 'stop'
                return

class DownloadFTPFile(DownloadFile):
    file = None
    def __init__(self, url, outputfile=None, outputdir=None, verbose=False, redirect_cycle_times=2, error_handler=None):
        self.url = url
        self.output_file_name = outputfile
        self.verbose = verbose
        self.domain_name = self.get_domain_name(url)
        self.outputdir = outputdir
        self.error_handler = error_handler
    
    def run(self):
        #global error_log
        if self.output_file_name is None:
            file_name = self.url[self.url.rfind('/') + 1:self.url.rfind('?')]
            file_name = file_name[:file_name.rfind('.')] + '.log'
        else:
            file_name = self.output_file_name
        
        if self.outputdir is not None:
            file_name = self.outputdir + '/' + file_name
        
        try:
            self.logger('Opening file %s ...' % file_name)
            self.output_file = codecs.open(file_name, 'w', encoding='utf-8')
            self.output_file.write(self.url + '\n')

            self.logger('Requesting %s ...' % self.url)
            self.output_file.write(self.get_nslookup(self.domain_name))
            self.output_file.write(self.get_host(self.domain_name))
            self.output_file.write(self.get_whois(self.domain_name))
            self.write_content_to_file()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            self.error_handler("I/O error({0}): {1}".format(e.errno, e.strerror))
            #error_log.write("%s : %s" % (self.url, str(e)))
        finally:
            self.logger('\tClosing file %s ...' % file_name)
            self.output_file.close()

    def write_content_to_file(self):
        self.output_file.write('\n<=HTTP BEGIN=>\n')
        filename = self.url[self.url.rfind('/') + 1:]
        path = self.url[7 + len(self.domain_name):len(self.url) - len(filename)]
        ftp = ftplib.FTP(self.domain_name)
        ftp.login("", "")
        if len(path) > 0:
            ftp.cwd(path)
        
        pre_time = time.time()
        with open('.' + filename, 'w+b') as f:
            ftp.retrbinary('RETR ' + filename, f.write)
        #ftp.retrbinary("RETR " + filename , self.output_file.write)
        ftp.close()
        total_time = time.time() - pre_time
        with open('.' + filename, 'r+b') as f2:
            for r in f2.readlines():
                self.output_file.write(r.decode('utf-8', errors='replace'))
        self.output_file.write('\n<=HTTP END=>\n')
        self.output_file.write(self.get_timer(total_time))

class DownloadHTTPFile(DownloadFile):
    file = None
    redirect_cycle = {}
    
    def __init__(self, url, outputfile=None, outputdir=None, verbose=False, redirect_cycle_times=2, error_handler=None, stream=False):
        self.url = url
        self.output_file_name = outputfile
        self.verbose = verbose
        self.redirect_cycle_times = redirect_cycle_times - 1
        self.domain_name = self.get_domain_name(url)
        self.outputdir = outputdir
        self.error_handler = error_handler
        self.stream = stream

    def run(self):
        #global error_log
        if self.output_file_name is None:
            file_name = self.url[self.url.rfind('/') + 1:self.url.rfind('?')]
            file_name = file_name[:file_name.rfind('.')] + '.log'
        else:
            file_name = self.output_file_name
        
        if self.outputdir is not None:
            file_name = self.outputdir + '/' + file_name
            
        pre_time = time.time()
        
        ua = UserAgent()
        user_agent = ua.firefox
        print '>>>>>>>>>>>>>>>>.'
        try:
            user_agent = ua.random
        except Exception as e:
            print str(e)
            try:
                user_agent = ua.random
            except Exception as e:
                sys.stderr.write('Can not use random agent.\n')
        
        print '>>>>>>>>>>>>>>>>.'
        headers = {'User-Agent': user_agent,'Connection': 'close', 'Accept-Encoding':''}
        
        try:
            response = requests.get(self.url, timeout=(30,180), headers=headers, stream=self.stream)
            #response.encoding = 'utf-8'
        except ConnectionError as e:
            self.error_handler("%s : ConnectionError" % (self.url))
            print "ConnectionError : %s" % str(e)
            return
        except TooManyRedirects as e:
            self.error_handler("%s : TooManyRedirects" % (self.url))
            print "TooManyRedirects : %s" % str(e)
            return
        except Timeout as e:
            # The request timed out while trying to connect to the remote server.
            # Requests that produced this error are safe to retry.
            self.error_handler("%s : Timeout" % (self.url))
            print "Timeout : %s" % e.message
            return
        except ContentDecodingError as e:
            self.error_handler("%s : ContentDecodingError" % (self.url))
            print "ContentDecodingError : %s" % e.message
            return
            '''
            if 'Accept-Encoding' not in headers:
                headers['Accept-Encoding'] = ''
                try:
                    response = requests.get(self.url, timeout=30, headers=headers, stream=True)
                except ContentDecodingError as e1:
                    self.error_handler("%s : ContentDecodingError" % (self.url))
                    print "ContentDecodingError : %s" % e.message
                    return
            '''
        except ChunkedEncodingError as e:
            # The server declared chunked encoding but sent an invalid chunk.
            self.error_handler("%s : ChunkedEncodingError" % (self.url))
            print "ChunkedEncodingError : %s" % e.message
            return
        except InvalidSchema as e:
            self.error_handler("%s : InvalidSchema" % (self.url))
            print "InvalidSchema : %s" % e.message
            return
        
        total_time = time.time() - pre_time
        self.logger('Checking alive ... : %s' % self.url)
        try:
            is_dead = not self.is_alive(response)
        except ConnectionError as e:
            print 'ssssssssssssssss'
            self.stream = False
            headers = {'User-Agent': user_agent, 'Accept-Encoding':''}
            try:
                response = requests.get(self.url, timeout=30, headers=headers, stream=self.stream)
            except Exception as e:
                self.error_handler("%s : ConnectionError" % (self.url))
                print "ConnectionError : %s" % str(e)
                return
            print 'dddddddddddddd'
            is_dead = not self.is_alive(response)
            
        if is_dead:
            self.error_handler(u'%s : %s' % (self.url, self.err))
            #error_log.write('%s : %s' % (self.url, self.err))
            print u'%s : %s' % (self.url, self.err)
            return
        try:
            self.logger('Opening file %s ...' % file_name)
            self.output_file = codecs.open(file_name, 'w', encoding='utf-8')
            self.output_file.write(self.url + '\n')

            self.logger('Requesting %s ...' % self.url)
            if self.is_redirect_cycle(response):
                self.output_file.write(self.get_redirect_warning())
            self.output_file.write(self.get_nslookup(self.domain_name))
            self.output_file.write(self.get_host(self.domain_name))
            self.output_file.write(self.get_whois(self.domain_name))
            self.download_file(response)
            self.output_file.write(self.get_timer(total_time))
        except IOError as e:
            self.error_handler("I/O error({0}): {1}".format(e.errno, e.strerror))
            sys.stderr.write("I/O error({0}): {1}\n".format(e.errno, e.strerror))
        except Exception as e:
            print 'ddddddddddddddddddddddddddddddddddd'
            print str(e)
        finally:
            self.logger('\tClosing file %s ...' % file_name)
            self.output_file.close()
            response.close()
            
    dont_download_err_codes = [403, 404, 500, 503]
    page_not_found_str = ['pila flag poles', 'error | cort.as', 'seite zur zeit nicht erreichbar', 'temporarily unavailable', 'ShrinkThisLink.com - Free link shrinker', 'monequipemobfree.com', 'Nom de domaine Gratuit avec Azote.org et SANS PUBLICITE', 'ooops', 'Warning! | There might be a problem with the requested link', '(This |)website (is|) (temporarily|currently) (unavailable|Not Available|suspended)', '(Website|site) Unavailable', "We're sorry! This account is currently unavailable | ROMARG", 'this page is not available', 'Suspend', 'Short.URL', 'Unauthorized Access']
    page_not_found_str_utf8 = [u'这个网站可出售', u'该网站正在出售', u'가비아 호스팅 서비스:웹호스팅,웹메일 호스팅,쇼핑몰호스팅,단독서버,동영상호스팅', u'무료호스팅', u'Хостинг-Центр']
    def is_alive(self, response):
        if 'Content-Type' in response.headers:
            if response.headers['Content-Type'].startswith('image') or response.headers['Content-Type'].startswith('application'):
                self.err = 'not web page({})'.format(response.headers['Content-Type'])
                return False
        #global error_log
        self.content = self._get_content(response)
        try:
            tree = html.fromstring(self.content)
            extract_titles = tree.xpath('//title/text()')
            '''
            soup = BeautifulSoup(self.content)
            extract_titles = soup.findAll('title')
            print extract_titles
            '''
        except XMLSyntaxError as e:
            print str(e)
            self.err = str(e)
            self.error_handler("%s : %s" % (self.url, str(e)))
            #error_log.write("%s : %s" % (self.url, str(e)))
            return False
        except ParserError as e:
            print str(e)
            self.err = str(e)
            self.error_handler("%s : %s" % (self.url, str(e)))
            return False
        except UnicodeDecodeError as e:
            tree = html.fromstring(get_unicode(self.content))
            extract_titles = tree.xpath('//title/text()')
        except Exception as e:
            if isinstance(self.content, unicode):
                tree = html.fromstring(self.content.encode('UTF-8'))
                extract_titles = tree.xpath('//title/text()')
        
        if extract_titles:
            for origin in extract_titles:
                extract_title = origin.encode('utf-8')
                for i in self.dont_download_err_codes:
                    if re.search('^(.*\d\D+|\D*)'+str(i)+'(\D+\d.*|\D*)$', extract_title):
                        self.logger('Error with http status code : %s' % str(i))
                        self.err = str(i)
                        return False
                if re.search('^.*suspended.*$', str(extract_title).lower()):
                    self.err = 'suspended'
                    self.logger('Error with http status code : ' + self.err)
                    return False
                if re.search('^.*linkbucks.com - get your share!.*$', str(extract_title).lower()):
                    self.err = 'suspended(linkbucks)'
                    self.logger('Error with http status code : ' + self.err)
                    return False
                if re.search('^contact support$', str(extract_title).lower()):
                    self.err = 'suspended'
                    self.logger('Error with http status code : ' + self.err)
                    return False
                if re.search('^(.* |.* can|.* could|)not(hing| be|) found.*$', str(extract_title).lower()):
                    self.err = 'page not found'
                    self.logger('Error with http status code : ' + self.err)
                    return False
                if re.search('^(.* |.*suspected |)phishing.*$', str(extract_title).lower()):
                    self.err = 'suspend(suspected phishing)'
                    self.logger('Error with http status code : ' + self.err)
                    return False
                for i in self.page_not_found_str:
                    if re.search('^.*' + i.lower() + '.*$', str(extract_title).lower()):
                        self.err = u'page not found({})'.format(i)
                        self.logger('Error with http status code : ' + self.err)
                        return False
                for i in self.page_not_found_str_utf8:
                    if i in origin:
                        self.err = u'page not found({})'.format(i)
                        self.logger(u'Error with http status code : {}'.format(self.err))
                        return False
                        
        for i in self.dont_download_err_codes:
            if i == response.status_code:
                self.logger('Error with http status code : %s' % str(i))
                self.err = str(i)
                return False
                
        return True

    def download_file(self, response):
        # if it has redirection before getting target url.
        if response.history:
            self.logger('\tRedirecting ...')
            for i in response.history:
                if i.url in self.redirect_cycle:
                    if self.redirect_cycle[i.url] > 0:
                        self.logger('\tRedirect to %s ...' % i.url)
                        self.redirect_cycle[i.url] -= 1
                        self.download_file(i)
                    else:
                        break
                else:
                    break
                    
        try:
            self.logger('\tDownloading %s ...' % response.url)
            self.output_file.write(self.get_headers(response))
            self.output_file.write(self.get_content(response))
        except Exception as e:
            self.error_handler("%s : %s" % (self.url, str(e)))

    def is_redirect_cycle(self, response):
        self.redirect_cycle = {}
        return self.redirect_cycle_test(response)

    def redirect_cycle_test(self, response):
        if response.url in self.redirect_cycle:
            if self.redirect_cycle[response.url] > self.redirect_cycle_times:
                return True
            else:
                self.redirect_cycle[response.url] += 1
        else:
            self.redirect_cycle[response.url] = 1
        test = False
        for r in response.history:
            test = test or self.redirect_cycle_test(r)
        return test

    def get_redirect_warning(self):
        s = "\n<=CYCLING REDIRECT WARNING BEGIN=>\n"
        s += "Cycle Redirect times:\n"
        for key in self.redirect_cycle:
            s += '%s:%d\n' % (key,self.redirect_cycle[key])
        s += "\n<=CYCLING REDIRECT WARNING END=>\n"
        return get_utf8(s)
        
    def __get_html_charset(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        metas = soup.find_all('meta')
        if metas:
            for meta in metas:
                if 'content' in meta.attrs:
                    contents = meta['content'].lower().split(';')
                    for content in contents:
                        if re.match('^.*charset.*$', content.lower(), re.IGNORECASE):
                            return content.split('=')[1].lower()
                elif 'charset' in meta.attrs:
                    return meta['charset']
        return None
        
    def _get_content(self, response):
        if not self.stream:
            charset = self.__get_html_charset(response)
            sys.stderr.write('Charset : {}\n'.format(charset))
            if charset != 'utf-8':
                response.encoding = charset
            return response.text
        download_time_limit = 60*60*10
        temp = u''
        pre_time = time.time()
        try:
            content_iter = response.iter_lines()
            origin = response.iter_lines()
        except requests.Timeout as e:
            print 'ddd'
            print temp
            print str(e)
        print response.encoding
        charset = 'utf-8'
        try:
            for row in content_iter:
                delta = time.time() - pre_time
                if delta > download_time_limit:
                    temp = ''
                    break
                else:
                    try:
                        '''
                        res = re.match('^.*<meta ([^>]*)>.*$', row.lower())
                        if res and re.match('^.*http-equiv=.Content-Type.*$', res.group(1).lower()) and res.group(1).find(';') != -1:
                            contents = res.group(1).split(';')
                            for content in contents:
                                if re.match('^.*charset.*$', content.lower()):
                                    charset = content.split('=')[0].lower()
                                    if charset != 'utf-8':
                                        response.encoding = charset
                                        temp = u''
                                        content_iter = origin
                                        continue
                                        '''
                        temp += row.decode('utf-8') + '\n'
                    except UnicodeDecodeError as e:
                        self.error_handler("%s : %s" % (self.url, str(e)))
                        if response.encoding and response.encoding.find(',') == -1:
                                temp += row.decode(response.encoding, errors='replace') + '\n'
                        elif response.encoding and response.encoding[:response.encoding.find(',')] != 'ISO-8859-1':
                                temp += row.decode(response.encoding[:response.encoding.find(',')], errors='replace') + '\n'
                        else:
                            temp += row.decode('utf-8', errors='ignore') + '\n'
        except requests.Timeout as e:
            print 'ddd'
            print temp
            print str(e)
        return temp
            
    def get_content(self, response):
        s = '\n<=HTTP BEGIN=>\n'
        s += self.content
        s += '\n<=HTTP END=>\n'
        return s
        
    def get_headers(self, response):
        s = '\n<=HEADER BEGIN=>\n'
        s += 'HTTP/%0.1f %d %s\n' % ((float)(response.raw.version/10.0), response.status_code, response.reason)
        for i in response.headers:
            s += '%s: %s\n' % (i, response.headers[i])
        s += '\n<=HEADER END=>\n'
        return get_utf8(s)
        #return s

start_number = 0
def crawl_from_file(file_path, outputdir=None, verbose=False, redirect_cycle_times=2, error_handler=None, stream=False):
    try:
      with codecs.open(file_path,'r', encoding='utf8') as f:
        for i, url in enumerate(f.readlines()):
           print '%d STARTING ... %s ' % (i + start_number, url.rstrip())
           a = downloader(url.rstrip(), outputfile=str(i + start_number), verbose=verbose, outputdir=outputdir, redirect_cycle_times=redirect_cycle_times, error_handler=error_handler, stream=stream)
           if a:
            a.run()
    except Exception as e:
        print str(e)

def downloader(url, outputfile=None, outputdir=None, verbose=False, redirect_cycle_times=2, error_handler=None, stream=False):
    if url.lower().startswith('http'):
        if url.lower().endswith('ico') or url.lower().endswith('jpg') or url.lower().endswith('png') or url.lower().endswith('pdf') or url.lower().endswith('bmp') or url.lower().endswith('tiff'):
            e = 'image file'
            if error_handler:
                error_handler("{} : {}".format(url, str(e)))
            sys.stderr.write("{} : {}\n".format(url, str(e)))
            return None
        return DownloadHTTPFile(url, outputdir=outputdir, outputfile=outputfile, verbose=verbose, redirect_cycle_times=redirect_cycle_times, error_handler=error_handler, stream=stream)
    elif url.lower().startswith('ftp:'):
        return DownloadFTPFile(url, outputdir=outputdir, outputfile=outputfile, verbose=verbose, error_handler=error_handler)

def get_domain_name(url):
    domain_name = url[url.find('//')+2:]
    domain_name = domain_name[:domain_name.find('/')]
    return domain_name

def help_message():
    print '''
    spider [-h]
    spider [-d OUTPUT_DIR][-i INPUTFILE]
    spider [-d OUTPUT_DIR][-u HTTP_URL]
'''

def get_unicode(s):
    if isinstance(s, unicode):
        return s
    return unicode(s, errors='ignore')

def get_utf8(s):
    if isinstance(s, str):
        return s
    return s.encode('utf-8')

def error_handler(msg):
    with codecs.open('error.log', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

error_log = None

def main(argv):
    input_file = None
    verbose = False
    stream = False
    url = None
    redirect_cycle_times = 2
    output_dir = None
    global start_number
    try:
        opts,args = getopt.getopt(argv, 'hi:vu:d:', ['help',' inputfile=', 'url=', 'outputdir=', 'startwith=', 'stream'])
        for opt,arg in opts:
            if opt in ('-v'):
                verbose = True
            elif opt in ('-h','--help'):
                help_message()
            elif opt in ('-i', '--inputfile='):
                input_file = arg
            elif opt in ('-u', '--url='):
                url = arg
            elif opt in ('-d', '--outputdir='):
                output_dir = arg
            elif opt in ('--startwith='):
                start_number = int(arg)
            elif opt in ('--stream'):
                stream = True
        #error_log = open('error.log','a')
        if input_file is not None:
            crawl_from_file(input_file, outputdir=output_dir, verbose=verbose, redirect_cycle_times=redirect_cycle_times, error_handler=error_handler, stream=stream)
        elif url is not None:
            downloader(url, verbose=verbose, outputdir=output_dir,redirect_cycle_times=redirect_cycle_times, error_handler=error_handler, stream=stream).run()
    except getopt.GetoptError as err:
        print str(err)
        help_message()
    except Exception as e:
        print str(e)
    finally:
        #error_log.close()
        sys.exit(2)
if __name__ == '__main__':
    main(sys.argv[1:])
    
