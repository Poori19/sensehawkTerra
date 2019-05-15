# coding=utf-8
import jwt
import traceback
import requests

from django.utils.functional import SimpleLazyObject
from django.utils.deprecation import MiddlewareMixin
from django.conf import LazySettings
from django.core.cache import cache

from okta_jwt.jwt import validate_token
from .constants import TOKEN_CACHE_TIME

settings = LazySettings()
import environ
env = environ.Env()


class OktaAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))

    @staticmethod
    def get_jwt_user(request):
        user_jwt = {}
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if token is not None:
            try:
                userData = OktaAuthenticationMiddleware.authenticateToken(token)
                user_jwt = userData
            except Exception as e: # NoQA
                traceback.print_exc()
        return user_jwt

    @staticmethod
    def okta_authentication(token):  

        dataResponse = {}
        try:
            issuer = "https://dev-612233.oktapreview.com/oauth2/default"       
            client_ids = ["0oajynre6wdHJZ2I20h7" ]
            audience = "api://default"                                                                                                                                                                                                   
            dataResponse = validate_token(token, issuer, audience, client_ids)                                                                                                                                                                                    
        except Exception as e: 
            traceback.print_exc() 
            print("error")
        return dataResponse
    
    @staticmethod
    def core_authentication(token):  

        dataResponse = {}
        # if present in cache, provide token 
        if cache.get(token):
            return cache.get(token)

        wholeToken = "Token " + token
        
        url = 'http://'+ env.str('COREURL')  + '/api/' + env.str('COREVERSION') + '/api-token-auth/'
        HEADERS = {'Authorization': wholeToken}
                    
        try:
            okta_response = requests.get(url,headers= HEADERS)
            # Consider any status other than 2xx an error
            if not okta_response.status_code // 100 == 2:
                raise Exception(okta_response.text, okta_response.status_code)
            dataResponse = okta_response.json()

            user = OktaAuthenticationMiddleware.get_user_data(dataResponse)

            # Adding JWK to the Cache
            CACHE_TIME = TOKEN_CACHE_TIME  # one hour
            cache.set(token, user, CACHE_TIME)
        except requests.exceptions.RequestException as e:
            # A serious problem happened, like an SSLError or InvalidURL
            raise Exception("Error: {}".format(str(e)))
        return user


    @staticmethod
    def get_user_data(dataResponse):  
        
        user = {}
        # set the email
        if dataResponse.get('email'):
            user['email'] = dataResponse['email']

        # set the userId
        if dataResponse.get('user_id'):
            user['uid'] = dataResponse['user_id']
        
        # set the status
        if dataResponse.get('status'):
            user['status'] = dataResponse['status']
        
        # set the role
        if dataResponse.get('user_role', { 'name': None }):
            user['role'] = dataResponse.get('user_role',{ 'name': None }).get('name')
        
        # set the organization
        if dataResponse.get('org', { 'uid': None }):
            user['organization'] = dataResponse.get('org', { 'uid': None }).get('uid')
        
        # set the is_manager
        if 'is_manager' in dataResponse:
            user['is_manager'] =  dataResponse['is_manager']
        
        # set the is_owner
        if 'is_owner' in dataResponse:
            user['is_owner']  = dataResponse['is_owner']
        
        # set the labels
        if dataResponse.get('labels', []):
            user['labels'] = list(map(lambda d: d.get('uid'), dataResponse.get('labels')))
        else:
            user['labels'] = []
        
        return user

        
    @staticmethod
    def authenticateToken(wholeToken):
        """ Authenticates the user with "Token" or "Access Token" """
        user = {}
        if wholeToken and len(wholeToken.split(" ")) == 2:
            tokenDict = wholeToken.split(" ")
            tokenType = tokenDict[0]
            token = tokenDict[1]   
                
            dataResponse = {}
            # verify from okta for the access token
            if tokenType.upper() == "JWT":
               dataResponse = OktaAuthenticationMiddleware.okta_authentication(token)
               user = OktaAuthenticationMiddleware.get_user_data(dataResponse)

            # verify from okta for the profile token
            if  tokenType.upper() == "TOKEN":
                user = OktaAuthenticationMiddleware.core_authentication(token)
        else:
            raise Exception("Error: {}".format("Token not sent or token sent without token type"))

        return user                                                               


        

