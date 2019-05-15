from cryptography.fernet import Fernet
from accounts.constants import ENCODE_KEY

from json import dumps
try:
    from urllib import urlencode, unquote
    from urlparse import urlparse, parse_qsl, ParseResult
except ImportError:
    # Python 3 fallback
    from urllib.parse import (
        urlencode, unquote, urlparse, parse_qsl, ParseResult
    )
    

class EncryptDecrypt():

    @staticmethod
    def encryptData(data):
        key = ENCODE_KEY.encode('utf8')     
        if type(data) == str:    
            data = data.encode('utf8') 
        f = Fernet(key)
        encryptedData = f.encrypt(data)
        return encryptedData.decode()

    @staticmethod
    def decryptData(encryptedData):
        key = ENCODE_KEY.encode('utf8') 
        if type(encryptedData) == str:    
            encryptedData = encryptedData.encode('utf8')        
        f = Fernet(key)
        decryptedData = f.decrypt(encryptedData)
        return decryptedData.decode()


    @staticmethod
    def get_parsed_object(url):

        # Unquoting URL first so we don't loose existing args
        url = unquote(url)
        # Extracting url info
        parsed_url = urlparse(url)

        return parsed_url

    @staticmethod
    def encryptAWSSignature(url):

        params = {} 
        parsed = EncryptDecrypt.get_parsed_object(url)
        # Extracting URL arguments from parsed URL
        get_args = parsed.query
        # Converting URL arguments to dict
        parsed_query_args = dict(parse_qsl(get_args))

        if parsed_query_args.get('X-Amz-Signature'):
            params['X-Amz-Signature'] = EncryptDecrypt.encryptData(parsed_query_args.get('X-Amz-Signature'))

        encryptedUrl = EncryptDecrypt.add_url_params(parsed,params)
        return encryptedUrl


    @staticmethod
    def add_url_params(parsed_url, params):
        """ Add GET params to provided URL being aware of existing.

        :param url: string of target URL
        :param params: dict containing requested params to be added
        :return: string with updated URL

        >> url = 'http://stackoverflow.com/test?answers=true'
        >> new_params = {'answers': False, 'data': ['some','values']}
        >> add_url_params(url, new_params)
        'http://stackoverflow.com/test?data=some&data=values&answers=false'
        """
       
        # Extracting URL arguments from parsed URL
        get_args = parsed_url.query
        # Converting URL arguments to dict
        parsed_get_args = dict(parse_qsl(get_args))
        # Merging URL arguments dict with new params
        parsed_get_args.update(params)

        # Bool and Dict values should be converted to json-friendly values
        # you may throw this part away if you don't like it :)
        parsed_get_args.update(
            {k: dumps(v) for k, v in parsed_get_args.items()
            if isinstance(v, (bool, dict))}
        )

        # Converting URL argument to proper query string
        encoded_get_args = urlencode(parsed_get_args, doseq=True)
        # Creating new parsed result object based on provided with new
        # URL arguments. Same thing happens inside of urlparse.
        new_url = ParseResult(
            parsed_url.scheme, parsed_url.netloc, parsed_url.path,
            parsed_url.params, encoded_get_args, parsed_url.fragment
        ).geturl()

        return new_url