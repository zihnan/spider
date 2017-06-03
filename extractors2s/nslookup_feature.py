import re
import datetime
import sys
from extractor import Extractor
class NslookupExtract(Extractor):
    def __init__(self, nslookup_str, **kwargs):
        self.nslookup = nslookup_str
        self.serial = self.get_serial()
        self.features = [self.get_dnsrecord, self.get_year_age]
    
    def get_canonical_name(self):
        name_list = set()
        for s in self.nslookup.split('\n'):
            if re.match('^.*canonical name = .*$', s):
                name_list.add(s.split(' ')[-1][:-1])
        return name_list
    
    def is_alias(self):
        name_list = self.get_canonical_name()
        if self.debug:
          print 'Canonical Name : ',
          print name_list
          print 'Number of Canonical Name : ',
          print len(name_list)
        return len(name_list) > 0
    
    def get_serial(self):
        for row in self.nslookup.split('\n'):
          if row.find(' = ') > 0:
            field, value = row.strip().rstrip().split(' = ')
            if field.lower() == 'serial':
              return value
        return None
    
    #6 DNS_Record
    def get_dnsrecord(self):
    	for row in self.nslookup.split('\n'):
	  if row.find('***') == 0:
	    return 0
     	return 1

    def is_weird_serial(self):
      if self.serial:
        return re.match('^\d{4}(0\d|10|11|12)[0-3]\d{3}$', self.serial) is None and re.match('^\d*$', self.serial) is None
      return True
      
    #7 Age of domain
    def get_year_age(self):
        year_age= self.get_day_age()
        if year_age>2:
            return 1
        elif year_age<1:
            return -1
        return 0

    def get_day_age(self):
      if self.serial:
        if self.debug:
          print 'Serial Date : ',
        if re.match('^[1-2]\d{3}(0[1-9]|10|11|12)(0[1-9]|[1-2]\d|3[0-2])\d{2}$', self.serial):
          sys.stderr.write(str(self.serial) + '\n')
          date = datetime.datetime.strptime(self.serial[:-2], '%Y%m%d')
          if self.debug:
            print 'Normal Format : ',
        elif re.match('^\d+$', self.serial):
          date = datetime.datetime.fromtimestamp(float(self.serial))
          if self.debug:
            print 'Timestamp : ',
        if self.debug:
          print date
	return int((datetime.datetime.now() - date).total_seconds() / 86400)/365
      return 0
