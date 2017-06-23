import urllib
import hashlib
import hmac
import datetime
import requests

AWSAccessKeyId='AKIAJWEULOS4W5J5ZFEQ'
AWSSecretKey='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'
domain_name='ntust.edu.tw'

class AlexaWebInfoRequest:
    def __init__(self, AWSAccessKeyID, AWSSecretKey, signature_method='HmacSHA256', signature_version='2'):
        self.id = AWSAccessKeyID
        self.key = AWSSecretKey
        self.method = signature_method
        self.version = signature_version
        self.signature = None
        self.url = None
    
    def query(self, domain):
        url = self.get_alexa_url(domain)
        return requests.get(url)
    
    def get_alexa_url(self, domain):
        self.url = self.sign_html(self.get_query_string(domain), self.get_signature(domain))
        return self.url
    
    def get_query_string(self, domain):
        self.query_string = self.__query(domain)
        return self.query_string
    
    def get_signature(self, domain):
        query_string = self.get_query_string(domain)
        self.signature = hmac.new(self.key, self.string_to_sign(query_string).encode('utf-8'), hashlib.sha256).digest().encode('base64').rstrip()
        return self.signature
    
    def sign_html(self, query, signature):
        return 'https://awis.amazonaws.com/?{query}&{signature}'.format(query=query, signature=urllib.urlencode({'Signature':signature}))
    
    def string_to_sign(self, query):
        temp = 'GET\n'
        temp += 'awis.amazonaws.com\n'
        temp += '/\n'
        temp += query
        return temp
    
    def __query(self, url):
        query = ''
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        amzdate = urllib.urlencode({'Timestamp':amzdate})
        query += 'AWSAccessKeyId={AWSAccessKeyId}&Action=UrlInfo&Count=10&ResponseGroup=Rank%2CLinksInCount&SignatureMethod={SignatureMethod}&SignatureVersion={Version}&Start=1&{Timestamp}&Url={Url}'.format(AWSAccessKeyId=self.id, SignatureMethod=self.method, Version=self.version, Timestamp=amzdate, Url=url)
        return query
    
def main():
    ov = AlexaWebInfoRequest(AWSAccessKeyId, AWSSecretKey)
    result = ov.query(domain_name)
    print result.text
    
if __name__ == '__main__':
    main()
    

