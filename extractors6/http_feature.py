# encoding=UTF-8
import codecs
import re
import json
import lxml
import numpy as np
import os
import sys
from bs4 import BeautifulSoup
from extractor import Extractor
from lxml import html
from sklearn.externals import joblib
from sklearn_extensions.extreme_learning_machines import ELMClassifier

class HttpExtractor(Extractor):
    frame = None
    redirect = None
    submit = None
    empty = False

    def __init__(self, html_str, **kwargs):
        self.html_str = html_str
        if 'url' in kwargs:
            self.url = str(kwargs['url']).rstrip()
            self.domain = self.get_domain_name(self.url)
        if 'tfidf_percent' in kwargs:
            if isinstance(kwargs['tfidf_percent'], float):
                self.tfidf_percent = kwargs['tfidf_percent']
            else:
                self.tfidf_percent = 0.9
        else:
            self.tfidf_percent = 0.9
        sys.stderr.write('TFIDF-percent: ' + str(self.tfidf_percent) + '\n')
        try:
            self.html_tree = BeautifulSoup(html_str, 'html.parser')
                    
        except lxml.etree.ParserError:
            self.empty = True
            sys.stderr.write('no a no link\n')
        
        striped_html_str = self.__striped_html_str(html_str)
        self.total_rows = len(striped_html_str.split('\n'))
        self.bytes = self.get_bytes(striped_html_str)
        self.style_block_rows = self.get_style_block_rows(striped_html_str)
        self.script_block_rows = self.get_script_block_rows(striped_html_str)
        self.script_block = self._get_script_block_rows()
        
        self.link_tags = self.get_link_tags()
        self.a_tags = self.get_a_tags()
        self.img_tags = self.get_img_tags()
        self.submit = self.get_submit()
        self.frame = self.get_iframe() + self.get_frame()
        self.redirect = self.get_redirect()
        self.script_tags = self.get_script_tags()
        self.title = self.get_title()
        
        #self.bytes_distribution = self.__get_bytes_distribution(html_str)
        
        self.features = [self.get_kbytes, self.is_frame, self.is_meta_redirect, self.is_meta_base64_redirect, self.same_extern_domain_script_rate, self.script_block_rate, self.style_block_rate, self.external_a_tag_same_domain,self.null_a_tag,self.same_external_domain_link_rate, self.same_external_domain_img_rate, self.get_title_feature, self.is_login_form]
        
    def is_login_form(self):
        return self.is_form() and not self.is_search()
        
    def is_search(self):
        is_search = False
        text_list = self._get_all_text()
        attr_list = self._get_all_attrs()
        pattern = '^(.*[^\w\d]+|)search(|[^\w\d]+.*)$'
        for text in text_list:
            if re.match(pattern, text, re.MULTILINE):
                is_search = True
                
        for attrs in attr_list:
            for attr_name in attrs:
                if isinstance(attrs[attr_name], list):
                    for value in attrs[attr_name]:
                        if re.match(pattern, value, re.MULTILINE):
                            is_search = True
                else:
                    if re.match(pattern, attrs[attr_name], re.MULTILINE):
                        is_search = True
        return is_search
        
    def _get_all_text(self):
        stripped_body3 = []
        if self.html_tree.body:
            for tag in self.html_tree.find_all(re.compile('^((?!script|style).)*$')):
                if tag.string and tag.string.strip():
                    if tag.parent.string and tag.string in tag.parent.string:
                        continue
                    stripped_body3.append(tag.string.strip().lower())
        return stripped_body3
    
    def _get_all_attrs(self):
        stripped3 = []
        if self.html_tree.body:
            for tag in self.html_tree.find_all(re.compile('^((?!script|style).)*$')):
                if tag.attrs:
                    stripped3.append(tag.attrs)
        return stripped3
        
    def is_seach(self):
        stripped_body3 = []
        count_vectorizer = CountVectorizer()
        if self.html_tree.body:
            for tag in self.html_tree.find_all(re.compile('^((?!script|style).)*$')):
                if tag.string and tag.string.strip():
                    if tag.parent.string and tag.string in tag.parent.string:
                        continue
                    stripped_body3.append(tag.string.strip())
                    sys.stderr.write(tag.string + '\n')
        if stripped_body3:
            x = count_vectorizer.fit_transform(['\n'.join(stripped_body3)])                                                    
            a = [i for i in x.toarray()[0]]
            for index, i in enumerate(a):
                term = count_vectorizer.get_feature_names()[index]
                if term not in test:
                    test[term] = i
                else:
                    test[term] += i
        else:
            sys.stderr.write('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
            sys.stderr.write(str(os.path.join(d, i)) + '\n')
            sys.stderr.write('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
        
    def __cal_tag_block(self, tag_name):
        #temp = 0
        temp = []
        html_str_list = self.html_str.split('\n')
        if not self.empty:
            block_begin = -1
            for i, row in enumerate(html_str_list):
                if row.find(tag_name) > 0:
                    l = len(re.findall('<'+tag_name, row.rstrip()))
                    r = len(re.findall('</'+ tag_name +'>', row.rstrip()))
                    if l > r:
                        block_begin = i
                    elif r > l and block_begin > 0:
                        #temp += i - block_begin + 1
                        temp += [j.rstrip() for j in html_str_list[block_begin:i - block_begin + 1]]
                        block_begin = -1
                    elif l > 0:
                        #temp += 1
                        temp.append(row.rstrip())
        return temp
        
    def _get_script_block_rows(self):
        return self.__cal_tag_block( 'script')
    
    def _get_form_in_javascript(self):
        if self.script_block_rows:
            block = '\n'.join(self.script_block)
            if re.match('^.*\.write(ln|)\(.*<form[^>]*>.*$', block.lower().rstrip(), re.MULTILINE):
                return True
        return False
    
    def get_form_in_javascript(self):
        number = 0
        if self.script_block_rows:
            form = self.get_form()
            form_name_list = [j for i in form if i.get('name') for j in i.get('name')]
            form_classname_list = [j for i in form if i.get('class') for j in i.get('class')]
            form_id_list = [j for i in form if i.get('id') for j in i.get('id')]
            for row in self.script_block:
                if re.search('^.*getElementById\(.([^)]*).\).*$', row.rstrip(), re.MULTILINE):
                    result = re.search('^.*getElementById\(.([^)]*).\).*$', row.rstrip(), re.MULTILINE)
                    text = result.group(1)
                    for i in form_id_list:
                        if i.strip() == text.strip():
                            number += 1
                            break
                elif re.search('^.*getElementsByTagName\(.form.\).*$', row.rstrip(), re.MULTILINE):
                    number += 1
                elif re.search('^.*getElementsByClassName\(.([^)]*).\).*$', row.rstrip(), re.MULTILINE):
                    result = re.search('^.*getElementsByClassName\(.([^)]*).\).*$', row.rstrip(), re.MULTILINE)
                    text = result.group(1)
                    for i in form_classname_list:
                        if i.strip() == text.strip():
                            number += 1
                            break
                elif re.search('^.*forms\[.([^\]]*).\].*$', row.rstrip(), re.MULTILINE):
                    result = re.search('^.*forms\[.([^\]]*).\].*$', row.rstrip(), re.MULTILINE)
                    text = result.group(1)
                    for i in form_name_list:
                        if i.strip() == text.strip():
                            number += 1
                            break
                elif re.match('^.*getElementsByName\(.([^)]*).\).*$', row.rstrip(), re.MULTILINE):
                    result = re.match('^.*getElementsByName\(.([^)]*).\).*$', row.rstrip(), re.MULTILINE)
                    text = result.group(1)
                    for i in form_name_list:
                        if i.strip() == text.strip():
                            number += 1
                            break
                elif re.search('^.*querySelector\(.([^)]*).\).*$', row.rstrip(), re.MULTILINE):
                    result = re.search('^.*querySelector\(.([^)]*).\).*$', row.rstrip(), re.MULTILINE)
                    text = result.group(1)
                    for i in form_classname_list + form_id_list:
                        if i.strip() == text.strip():
                            number += 1
                            break
        return number > 0
        
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
        self.url = url
        sys.stderr.write(self.url)
        return self

    def get_url(self):
        return self.url

    def get_iframe(self):
        if not self.empty:
            return self.html_tree.find_all('iframe')
        return []

    def get_frame(self):
        if not self.empty:
            return self.html_tree.find_all('frame')
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
            for i in self.html_tree.find_all('meta'):
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
            return self.html_tree.find_all(type="submit")
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
            return self.html_tree.find_all('a')
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
            return self.html_tree.find_all('link')
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
            return self.html_tree.find_all('img')
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
            return self.html_tree.find_all('form')
        return None
    
    def is_form(self):
       if self.get_form() or self._get_form_in_javascript():
           return True
       return False
    
    def get_script_tags(self):
        if not self.empty:
            return self.html_tree.find_all('script')
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
        
        
    def __split_title(self, title):
        delimiter = ['/', '?', '.', '=', '-', '_', '!',':', ';', '|', '(', ')', ',', '@', '"', "'", '[', ']',u'，', u'、', u'！', u'【', u'】', u'“', u'”', u'・', u'『', u'』', u'｜', u'‹', u'›', u'丨', u'¥']
        tf_test = []
        for t in title:
            t = t.strip()
            for d in delimiter:
                t = t.replace(d, ' ')
            tf_test += [i.lower() for i in t.split(' ') if i]
        return tf_test
        
    def get_title(self):
        if self.empty:
            return []
        '''
        return self.html_tree.xpath('//title/text()')
        '''
        result = self.html_tree.find_all('title')
        if result:
            result = [i.text for i in result if i.text.strip()]
            return result
        return []
        
    def get_title_feature(self):
        if not self.title:
            return 0
        with codecs.open('tfidf2 {:d}% term'.format(int(self.tfidf_percent * 100)), 'r', encoding='utf-8') as f:
            # nothing
            tf_position = json.loads(f.readline().rstrip())
            # get tf-idf terms
            tf_term = f.readline().rstrip().split(' ')
            sys.stderr.write('Load tfidf-{:d}%-elm.model\n'.format(int(self.tfidf_percent * 100)))
            # loading completed model
            elm = joblib.load('tfidf-{:d}%-elm.model'.format(int(self.tfidf_percent * 100)))
            
            if self.title:
                title_list = self.__split_title(self.title)
            else:
                return 0
            
            # initializing a empty features vector of elm model
            elm_vector = [[0] * len(tf_term)]
            # mapping data into the features vector of elm model
            sys.stderr.write('term :\t')
            for index, t in enumerate(tf_term):
                if t.lower() in title_list:
                    sys.stderr.write(t.lower() + ' ')
                    elm_vector[0][index] = 1
                    
            sys.stderr.write('\n')
            # classifing the title feature where in the elm model
            score = elm.predict(np.array(elm_vector))
            # must convert to list, because the output of elm.predict is numpy.array
            # which cannot using to train other model directly
            score = score.tolist()
            if isinstance(score, list):
                return score[0]
            else:
                return score
    '''
    def title_features(self):
        title_list = self.html_tree.xpath('//title/text()')
        with codecs.open('tfidf-term', 'r', encoding='utf-8') as f:
            f.readline()
            tfidf_set = f.readline().rstrip().split(' ')
        temp = [0] * len(tfidf_set)
        if not title_list:
            return temp
        else:
            delimiter = ['/', '?', '.', '=', '-', '_', '!',':', ';', '|', '(', ')', ',', '@', '"', "'", '[', ']',u'，', u'、', u'！', u'【', u'】', u'“', u'”', u'・', u'『', u'』', u'｜', u'‹', u'›', u'丨', u'¥']
            for title in title_list:
                for d in delimiter:
                    title = title.replace(d, ' ')
                for t in title.split().split(' '):
                    if t in tfidf_set:
                        temp[tfidf_set.index(t)] += 1
            return temp
        '''
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
        self.title += other.title
        '''
        for i in range(256):
            self.bytes_distribution[i] += other.bytes_distribution[i]
        '''
        return self
