import re
import lxml
import os
import sys
from lxml import html

from extractor import Extractor

import pprint

class HttpExtractor(Extractor):
    empty = False

    def __init__(self, html_str, **kwargs):
        try:
            self.html_str = html_str
            self.html_tree = html.fromstring(html_str)
            if 'url' in kwargs:
              self.url = str(kwargs['url']).rstrip()
              self.domain = self.get_domain_name(self.url)
        except lxml.etree.ParserError:
            self.empty = True
            sys.stderr.write('no a no link\n')
        
        striped_html_str = self.__striped_html_str(html_str)
        self.total_rows = len(striped_html_str.split('\n'))
        self.script_block_rows = self._get_script_block_rows(striped_html_str)
        self.embed = self._get_embed_tags()
        
        self.features = [getattr(self,i) for i in dir(self.__class__) if i.startswith('get') and 'get_url' not in i and 'get_domain_name' not in i]

        
    # New Hybrid Features
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
        
    def __cal_tag_block_rows(self, tag_name):
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
        
    def _get_script_block_rows(self, html_str):
        return self.__cal_tag_block_rows( 'script')
        
    def script_block_rate(self):
        if self.total_rows > 0:
            return float(self.script_block_rows)/float(self.total_rows)
        return 0.0
    
    def _get_number_of_object(self, obj):
        number = 0
        for row in self.html_str.split('\n'):
            for r in row.rstrip().split(';'):
                if re.match('^.*' + obj + '.*$', r.strip(), re.IGNORECASE):
                    number += 1
        return number
        
    # F1
    def get_FileSystemObject(self):
        return self._get_number_of_object( 'Scripting\.FileSystemObject')
        
    # F2
    def get_ExcelApplication(self):
        return self._get_number_of_object( 'Excel\.Application')
        
    # F3
    def get_WScriptShell(self):
        return self._get_number_of_object( 'WScript\.Shell')
        
    # F4
    def get_ADODBStream(self):
        return self._get_number_of_object( 'ADODB\.Stream')
        
    # F5
    def get_MicrosoftXMLDOM(self):
        return self._get_number_of_object( 'Microsoft\.XMLDOM')
    
    def _get_embed_tags(self):
        if not self.empty:
            return self.html_tree.xpath('//embed')
        return []
    
    # F6
    def get_embed_tags(self):
        if not self.empty:
            return len(self.embed)
        return 0
        
    # F7
    def get_applet_tags(self):
        if not self.empty:
            return len(self.html_tree.xpath('//applet'))
        return 0
    
    # F8
    def get_WordApplication(self):
        return self._get_number_of_object( 'Word\.Application')
        
    # 9 not sure
    def get_embed_src_length(self):
        length = 0
        if self.embed:
            for node in self.embed:
                url = node.get('src')
                length += len(url)
        return length
        
    # F10
    def get_iframe(self):
        if not self.empty:
            return len(self.html_tree.xpath('//iframe'))
        return 0
    
    # F11
    def get_frame(self):
        if not self.empty:
            return len(self.html_tree.xpath('//frame'))
        return 0
        
    # F12
    def get_outofplace_tags(self):
        if not self.empty:
            regexpNS = "http://exslt.org/regular-expressions"
            return len(self.html_tree.xpath('//*[re:match(@style, "visibility:.*hidden")]', namespaces={'re': regexpNS}) + self.html_tree.xpath('//*[@type="hidden"]') + self.html_tree.xpath('//*[@hidden]') + self.html_tree.xpath('//*[re:match(@style, "display:.*none")]', namespaces={'re': regexpNS}))
        return 0
    
    # F13
    def get_form(self):
        if not self.empty:
            return len(self.html_tree.xpath('//form'))
        return 0
        
    # F14
    def get_input(self):
        if not self.empty:
            return len(self.html_tree.xpath('//input'))
        return 0
    
    # F15
    def get_MSXML21(self):
        return self._get_number_of_object( 'MSXML2\.XMLHTTP')
    
    # F16 not sure
    def get_frequent_head_title_body(self):
        return self._get_number_of_object( '<head>') + self._get_number_of_object( '<title>') + self._get_number_of_object( '<body>')
        
    # F17 not sure
    def get_meta(self):
        return self._get_number_of_object( '<meta .*index.php?Sp1=')
        
    # F18
    def get_object_codebase(self):
        if not self.empty:
            return len(self.html_tree.xpath('//object/@codebase'))
        return 0
        
    # F19
    def get_applet_codebase(self):
        if not self.empty:
            return len(self.html_tree.xpath('//applet/@codebase'))
        return 0
        
    # F20
    def get_link_href(self):
        if not self.empty:
            return len(self.html_tree.xpath('//link/@href'))
        return 0
    
    # F21
    def get_void_link_in_form(self):
        if not self.empty:
            return len(self.html_tree.xpath('//form/a[@href=""]') + self.html_tree.xpath('//form/a[@href="#"]'))
        return 0
        
    # F22
    def get_out_link_in_form(self):
        if not self.empty:
            href_list = self.html_tree.xpath('//form/a/@href')
            return len([node for node in href_list if node != '' and node != '#'])
        return 0
        
    # F23
    def get_form_in_javascript(self):
        if self.script_block_rows:
            number = 0
            form_name_list = self.html_tree.xpath('//form/@name')
            form_classname_list = self.html_tree.xpath('//form/@class')
            form_id_list = self.html_tree.xpath('//form/@id')
            for row in self.script_block_rows:
                if re.match('^.*getElementById\(.*$', row.rstrip()):
                    for i in form_id_list:
                        if i in row:
                            number += 1
                            break
                elif re.match('^.*getElementsByTagName\(.form.*$', row.rstrip()):
                    number += 1
                elif re.match('^.*getElementsByClassName\(.*$', row.rstrip()):
                    for i in form_classname_list:
                        if i in row:
                            number += 1
                            break
                elif re.match('^.*forms\[.*$', row.rstrip()) or re.match('^.*getElementsByName\(.*$', row.rstrip()):
                    for i in form_name_list:
                        if i in row:
                            number += 1
                            break
                elif re.match('^.*querySelector\(.*$', row.rstrip()):
                    for i in form_classname_list + form_id_list:
                        if i in row:
                            number += 1
                            break
        return 0
        
    # F24 not sure
    def get_input_in_javascript(self):
        if self.script_block_rows:
            number = 0
            input_name_list = self.html_tree.xpath('//input/@name')
            input_classname_list = self.html_tree.xpath('//input/@class')
            input_id_list = self.html_tree.xpath('//input/@id')
            for row in self.script_block_rows:
                if re.match('^.*getElementById\(.*$', row.rstrip()):
                    for i in input_id_list:
                        if i in row:
                            number += 1
                elif re.match('^.*getElementsByTagName\(.input.*$', row.rstrip()):
                    number += 1
                elif re.match('^.*getElementsByClassName\(.*$', row.rstrip()):
                    for i in input_classname_list:
                        if i in row:
                            number += 1
                elif re.match('^.*getElementsByName\(.*$', row.rstrip()):
                    for i in input_name_list:
                        if i in row:
                            number += 1
        return 0
        
    # F25
    def get_javascript_length(self):
        if self.script_block_rows:
            return sum([len(row) for row in self.script_block_rows])
        return 0
        
    # F26
    def get_javascript_function_calls(self):
        number = 0
        if self.script_block_rows:
            for row in self.script_block_rows:
                number += len(re.findall('\(', row.rstrip()))
            return number    
        return 0
        
    # F27
    def get_javascript_rows(self):
        if self.script_block_rows:
            return len(self.script_block_rows)
        return 0
        
    # F28 not sure
    def get_javascript_length2(self):
        number = 0
        if self.script_block_rows:
            for row in self.script_block_rows:
                number += len(re.findall('\(', row.rstrip()))
            return number    
        return 0
        
    # F29
    def get_long_javascript_variable(self):
        temp = False
        if self.script_block_rows:
            for row in self.script_block_rows:
                p = row.find('=')
                temp = p > 12
        return temp
        
    # F30
    def get_long_javascript_function(self):
        temp = False
        if self.script_block_rows:
            for row in self.script_block_rows:
                for i in row.split(';'):
                    result = re.match('^.*function ([^\(]*)\(.*$', i)
                    if result and result.group(1) > 35:
                        temp = True
        return temp
        
    # F31
    def get_fromChartCode(self):
        return self._get_number_of_object( 'fromCharCode\(')
        
    # F32
    def get_attachEvent(self):
        return self._get_number_of_object( 'attachEvent\(')
        
    # F33
    def get_eval(self):
        return self._get_number_of_object( 'eval\(')
        
    # F34
    def get_escap(self):
        return self._get_number_of_object( 'escap\(')
        
    # F35
    def get_dispatchEvent(self):
        return self._get_number_of_object( 'dispatchEvent\(')
        
    # F36
    def get_SetTimeout(self):
        return self._get_number_of_object( 'SetTimeout\(')
        
    # F37
    def get_exec(self):
        return self._get_number_of_object( 'exec\(')
        
    # F38
    def get_pop(self):
        return self._get_number_of_object( 'pop\(')
        
    # F39
    def get_replaceNode(self):
        return self._get_number_of_object( 'replaceNode\(')
        
    # F40
    def get_onerror1(self):
        return self._get_number_of_object( 'onerror\(')
        
    # F41
    def get_onload(self):
        return self._get_number_of_object( 'onload\(')
    
    # F42
    def get_onunload(self):
        return self._get_number_of_object( 'onunload\(')
        
    # F43
    def get_script1(self):
        return self._get_number_of_object( '<script>')
        
    # F44
    def get_onclick(self):
        return self._get_number_of_object( '<div onclick=.window.open\("')
    
    # F45
    def get_script2(self):
        return self._get_number_of_object( '<script>')
        
    # F46
    def get_MSXML22(self):
        return self._get_number_of_object( 'MSXML2\.XMLHTTP')
        
    # F47
    def get_onerror2(self):
        return self._get_number_of_object( 'onerror\(')
        
    # F48
    def get_SetInterval(self):
        return self._get_number_of_object( 'SetInterval\(')
        
    def __add__(self, other):
        self.html_str += other.html_str
        try:
            self.html_tree = html.fromstring(self.html_str)
        except lxml.etree.ParserError:
            self.empty = True
        self.script_block_rows += other.script_block_rows
        self.total_rows += other.total_rows
        
        self.script_block_rows += other.script_block_rows
        self.embed = other.embed
        
        return self
