import re
from lxml import html
from extractor import Extractor

class HostExtract(Extractor):
    def __init__(self, host_str, **kwargs):
        self.ipv4_address_list = []
        self.ipv6_address_list = []

        for row in host_str.split('\n'):
            if row:
                cols = row.split(' ')
                if cols[2] == 'address':
                    self.ipv4_address_list.append(cols[3])
                elif cols[2] == 'IPv6':
                    self.ipv6_address_list.append(cols[4])
                    
        self.features = [self.ipv4_numbers, self.ipv6_numbers]

    def ipv4_numbers(self):
        return len(self.ipv4_address_list)

    def ipv6_numbers(self):
        return len(self.ipv6_address_list)
        
