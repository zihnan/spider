import re
import lxml
import os
import sys
from lxml import html

from extractor import Extractor

class HttpExtractor(Extractor):
    frame = None
    redirect = None
    submit = None
    empty = False

    def __init__(self, html_str, **kwargs):
        try:
            self.html_tree = html.fromstring(html_str)
            if 'url' in kwargs:
              self.url = str(kwargs['url']).rstrip()
              self.domain = self.get_domain_name(self.url)
        except lxml.etree.ParserError:
            self.empty = True
            sys.stderr.write('no a no link\n')
        
        striped_html_str = self.__striped_html_str(html_str)
        self.total_rows = len(striped_html_str.split('\n'))
        self.bytes = self.get_bytes(striped_html_str)
        self.style_block_rows = self.get_style_block_rows(striped_html_str)
        self.script_block_rows = self.get_script_block_rows(striped_html_str)
        
        self.link_tags = self.get_link_tags()
        self.a_tags = self.get_a_tags()
        self.img_tags = self.get_img_tags()
        self.submit = self.get_submit()
        self.frame = self.get_iframe() + self.get_frame()
        self.redirect = self.get_redirect()
        self.script_tags = self.get_script_tags()
        
        self.bytes_distribution = self.__get_bytes_distribution(html_str)
        
        self.features = [self.get_kbytes, self.is_frame, self.is_meta_redirect, self.is_meta_base64_redirect, self.is_form, self.is_input_submit, self.is_button_submit, self.same_extern_domain_script_rate, self.script_block_rate, self.style_block_rate, self.external_a_tag_same_domain,self.null_a_tag,self.same_external_domain_link_rate, self.same_external_domain_img_rate]
        
    def __get_bytes_distribution(self, html_str):
        temp = [0]*256
        for line in html_str.split('\n'):
            for c in line:
                temp[ord(c)] += 1
        return temp
        
    def get_bytes_distribution(self):
        if not self.empty:
            return self.bytes_distribution
        return []
        
    def get_bytes(self, html_str):
        return len(html_str)
    
    def get_kbytes(self):
        return float(self.bytes)/1024.0
        
    def __striped_html_str(self, html_str):
        temp = html_str.rstrip()
        striped_html_str = []
        for row in temp.split('\n'):
            if re.match('^<!--.*(-->.*<!--)+.*-->$', row.rstrip()):
                striped_html_str.append(row.rstrip())
            elif re.match('^<!--.*-->$', row.rstrip()):
                continue
            else:
                striped_html_str.append(row.rstrip())
        return '\n'.join(striped_html_str)

    def __cal_tag_block_rows(self, html_str, tag_name):
        temp = 0
        if not self.empty:
            block_begin = -1
            for i, row in enumerate(html_str.split('\n')):
                if row.find(tag_name) > 0:
                    l = len(re.findall('<'+tag_name, row.rstrip()))
                    r = len(re.findall('</'+ tag_name +'>', row.rstrip()))
                    if l > r:
                        block_begin = i
                    elif r > l and block_begin > 0:
                        temp += i - block_begin + 1
                        block_begin = -1
                    elif l > 0:
                        temp += 1
        return temp
        

    def get_script_block_rows(self, html_str):
        return self.__cal_tag_block_rows(html_str, 'script')
        
    def script_block_rate(self):
        if self.total_rows > 0:
            return float(self.script_block_rows)/float(self.total_rows)
        return 0.0
        
    def get_style_block_rows(self, html_str):
        return self.__cal_tag_block_rows(html_str, 'style')

    def style_block_rate(self):
        if self.total_rows > 0:
            return float(self.style_block_rows)/float(self.total_rows)
        return 0.0

    def set_url(self, url):
        print 'sdllsl'
        self.url = url
        print self.url
        return self

    def get_url(self):
        return self.url

    def get_iframe(self):
        if not self.empty:
            return self.html_tree.xpath('//iframe')
        return []

    def get_frame(self):
        if not self.empty:
            return self.html_tree.xpath('//frame')
        return []

    def frame_feature(self):
        frame = self.get_frame()
        if frame:
            return len(frame)
        else:
            return 0
            
    #7
    def is_frame(self):
        if self.frame:
            return True
        return False

    def get_redirect(self):
        if not self.empty:
            redirect = []
            for i in self.html_tree.xpath('//meta'):
              if i.get('http-equiv') is not None:
                if re.match('^refresh$', i.get('http-equiv'), re.IGNORECASE):
                    redirect.append(i)
            # return self.html_tree.xpath('//meta[@http-equiv="refresh"]') + self.html_tree.xpath('//meta[@http-equiv="Refresh"]') + self.html_tree.xpath('//meta[@http-equiv="REFRESH"]')
            return redirect
        return []
    
    def is_meta_base64_redirect(self):
        for i in self.redirect:
            if re.match('^.*base64.*$', i.get('content').lower(), re.IGNORECASE):
                return True
        return False
        
    def is_meta_redirect(self):
        if self.is_redirect() and not self.is_meta_base64_redirect():
            return True
        return False
    
    def redirect_feature(self):
        redirect = self.get_redirect()
        if redirect:
            return len(redirect)
        else:
            return 0

    #8
    def is_redirect(self):
        if self.redirect:
            return True
        return False

    def submit_feature(self):
        sumit = self.get_submit()
        if submit:
            return len(submit)
        else:
            return 0

    def get_submit(self):
        if not self.empty:
            return self.html_tree.xpath('//*[@type="submit"]')
        return []
    
    def is_input_submit(self):
        for i in self.submit:
          if i.tag == 'input':
            return True
        return False

    def is_button_submit(self):
        for i in self.submit:
          if i.tag == 'button':
            return True
        return False
            
    #9
    def is_submit(self):
        if self.submit:
            return True
        return False
    
    def get_a_tags(self):
        if not self.empty:
            return self.html_tree.xpath('//a')
        return []
    
    def external_a_tag_same_domain(self):
        if self.empty:
            return 0.0
        urls = {}
        total = 0
        null_url = 0
        for node in self.a_tags:
            url = node.get('href')
            total += 1
            if url and url != '#' and url != '':
                domain_name = self.get_domain_name(url)
                if domain_name in urls:
                    urls[domain_name] += 1
                else:
                    urls[domain_name] = 1
            else:
                null_url += 1
        m = 0
        for domain_name in urls:
            if urls[domain_name] > m and domain_name != '.' and domain_name != self.domain:
                m = urls[domain_name]
        if total > 0:
            return float(m)/float(total)
        return 0
    
    def null_a_tag(self):
        if self.empty:
            return 0.0
        urls = {}
        total = 0
        null_url = 0
        for node in self.a_tags:
            url = node.get('href')
            total += 1
            if url and not url.startswith('#') and url != '' and 'void(' not in url:
                domain_name = self.get_domain_name(url)
                if domain_name in urls:
                    urls[domain_name] += 1
                else:
                    urls[domain_name] = 1
            else:
                null_url += 1
        m = null_url
        if total > 0:
            return float(m)/float(total)
        return 0
    
    def get_link_tags(self):
        if not self.empty:
            return self.html_tree.xpath('//link')
        return []
    
    def same_external_domain_link_rate(self):
        if self.empty:
            return 0.0
        urls = {}
        total = 0
        null_url = 0
        for node in self.link_tags:
            url = node.get('href')
            total += 1
            if url and url != '#' and url != '':
                domain_name = self.get_domain_name(url)
                if domain_name in urls:
                    urls[domain_name] += 1
                else:
                    urls[domain_name] = 1
            else:
                null_url += 1
        
        m = 0
        for domain_name in urls:
            if urls[domain_name] > m and domain_name != '.' and domain_name != self.domain:
                m = urls[domain_name]
        if total > 0:
            return float(m)/float(total)
        return 0
    
    def get_img_tags(self):
        if not self.empty:
            return self.html_tree.xpath('//img')
        return []
    
    def same_external_domain_img_rate(self):
        if self.empty:
            return 0.0
        urls = {}
        total = 0
        null_url = 0
        for node in self.img_tags:
            url = node.get('src')
            total += 1
            if url:
                domain_name = self.get_domain_name(url)
                if domain_name in urls:
                    urls[domain_name] += 1
                else:
                    urls[domain_name] = 1
            else:
                null_url += 1
        m = 0
        for domain_name in urls:
            if urls[domain_name] > m and domain_name != '.' and domain_name != self.domain:
                m = urls[domain_name]
        if total > 0:
            return float(m)/float(total)
        else:
            return 0
    
    def get_form(self):
        if not self.empty:
            return self.html_tree.xpath('//form')
        return None
    
    def is_form(self):
       if self.get_form():
           return True
       return False
    
    def get_script_tags(self):
        if not self.empty:
            return self.html_tree.xpath('//script')
        return []

    def same_extern_domain_script_rate(self):
        if self.empty:
            return 0.0
        temp = {}
        total = 0
        null_url = 0
        for tag in self.script_tags:
            url = tag.get('src')
            total += 1
            if url:
                domain_name = self.get_domain_name(url)
                if domain_name not in temp:
                    temp[domain_name] = 1
                else:
                    temp[domain_name] +=1
            else:
                null_url += 1
        m = 0
        for domain in temp:
            if domain != '.' and temp[domain] > m and domain != self.domain:
                m = temp[domain]
                
        if total > 0:
            return float(m)/float(total)
        return 0.0
        
    def __add__(self, other):
        self.a_tags += other.a_tags
        self.link_tags += other.link_tags
        self.img_tags += other.img_tags
        self.submit += other.submit
        self.frame += other.frame
        self.redirect += other.redirect
        self.style_block_rows += other.style_block_rows
        self.script_block_rows += other.script_block_rows
        self.total_rows += other.total_rows
        self.script_tags += other.script_tags
        self.bytes += other.bytes
        
        for i in range(256):
            self.bytes_distribution[i] += other.bytes_distribution[i]
        
        return self
