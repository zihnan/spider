import itertools
import re

class Extractor(object): 
    features = []
    verbose = False
    debug = False
    url = None
    domain =None

    def __init__(self, data, **kwargs):
        pass

    def set_url(self, url):
        pass

    def get_url(self):
        pass

    def extract(self):
        if self.verbose:
            print self.__class__.__name__, ' ==> ',
            print [i.__name__ for i in self.features]
            print [i() for i in self.features]
        return [i() for i in self.features]
    
    # check whether contains 'JavaScript:document.location.href'
    def is_javascript_url(self, url):
        if url.lower().startswith('javascript:'):
            return True
        return False
    
    def set_verbose(self, enable):
        self.verbose = enable
        return self
        
    def set_debug(self, enable):
        self.debug = enable
        return self
        
    def __add__(self, other):
        pass
    
    def get_url_from_javascript_url(self, javascript_url):
        pattern = '.{3,5}://.*'
        qout = javascript_url.find("'")
        double_qout = javascript_url.find('"')
        if qout > 0:
            url = javascript_url[qout + 1:]
            url = url[:url.rfind("'")]
        elif double_qout > 0:
            url = javascript_url[double_qout + 1:]
            url = url[:url.rfind('"')]
        else:
            return None
        
        if re.match(pattern, url):
            return url
        else:
            return None
    
    def get_domain_name(self, url):
        double_escape = url.find('//')
        if double_escape < 0:
            return '.'
        domain_name = url[url.find('//')+2:]
        escape = domain_name.find('/')
        quest_mark = domain_name.find('?')
        if escape > 0:
            domain_name = domain_name[:escape]
        else:
            if quest_mark > 0:
                domain_name = domain_name[:quest_mark]
        
        commas = domain_name.rfind(':')
        if commas > 0:
            domain_name = domain_name[:commas]
        
        at_sym = domain_name.find('@')
        if at_sym > 0:
            domain_name = domain_name[at_sym + 1:]
        return domain_name
        
