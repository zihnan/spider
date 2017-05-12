import itertools
import re

class Extractor(object): 
    features = []
    verbose = False
    debug = False
    numeric = False
    url = None
    domain =None

    def __init__(self, data, **kwargs):
        pass

    def set_url(self, url):
        pass

    def get_url(self):
        pass
    
    def __to_numeric(self, features):
        temp = []
        for f in features:
            if isinstance(f, bool):
                temp.append(int(f))
            else:
                temp.append(f)
        return temp
        
    def extract(self):
        temp = [i() for i in self.features]
        if self.numeric:
            temp = self.__to_numeric(temp)
        if self.verbose:
            print '{name} length: {len}'.format(name=self.__class__.__name__, len=len(temp))
            print '{:>10} ==> {}'.format('', str([i.__name__ for i in self.features]))
            print '{:>10} ==> {}'.format('', str(temp))
        return temp
    
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
    
    def set_numeric(self, enable):
        self.numeric = enable
        return self
    
    def set_quiet(self,enable):
        pass
    
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
        if domain_name.startswith('www.'):
            domain_name = domain_name[4:]
        return domain_name
        
