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


from .userdata import users

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
    def authenticateToken(wholeToken):
        """ Authenticates the user with "Token" or "Access Token" """
        user = {}
        if wholeToken and len(wholeToken.split(" ")) == 2:
            tokenDict = wholeToken.split(" ")
            tokenType = tokenDict[0]
            token = tokenDict[1]   
                    
            # verify from okta for the access token
            if tokenType.upper() == "BEARER":
                try:
                    issuer = "https://dev-802525.okta.com/oauth2/default"       
                    #client_ids = ["0oad5bqrmkOMOxq8X356"]
                    #audience = "api://default" 

                    #issuer = env.str('OKTA_ISSUER_URL') 
                    client_ids = [env.str('CLIENT_ID')  ]
                    audience = env.str('OKTA_AUTH_SERVER')                                                                                                                                                                                                     
                    dataResponse = validate_token(token, issuer, audience, client_ids)  
        
                    # just for purpose of testing/remove after testing
                    #  dataResponse = users[1]
            
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
                    if dataResponse.get('role', { 'name': None }):
                        user['role'] = dataResponse.get('user_role', {}).get('name', None)
                    
                    # set the organization
                    if dataResponse.get('org', { 'uid': None }):
                        user['organization'] = dataResponse.get('org').get('uid')
                    
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

                except Exception as e: 
                    traceback.print_exc() 
                    print("error")

            # verify from okta for the profile token
            if  tokenType.upper() == "TOKEN":


                # if exist in cache, return cache
                if cache.get(token):
                    return cache.get(token)

                # make the request to okta
                else:
                    # OKTA_TOKEN = env('OKTA_TOKEN')
                    # HEADERS = {'Authorization': 'SSWS {}'.format(OKTA_TOKEN)}
                    # PROFILE_SEARCH_URL = env('PROFILE_SEARCH_URL')                              
                    # url = '{} "{}"'.format(PROFILE_SEARCH_URL,token)


                    url = 'http://'+ env.str('COREURL')  + '/api/' + env.str('COREVERSION') + '/api-token-auth/'
                    HEADERS = {'Authorization': wholeToken}


                    try:
                        okta_response = requests.get(url,headers= HEADERS)
                        # Consider any status other than 2xx an error
                        if not okta_response.status_code // 100 == 2:
                            raise Exception(okta_response.text, okta_response.status_code)
                    except requests.exceptions.RequestException as e:
                        # A serious problem happened, like an SSLError or InvalidURL
                        raise Exception("Error: {}".format(str(e)))

                    dataResponse = okta_response.json()

                    if not len(dataResponse):
                        raise Exception("Error: Could not find user for token: {}".format(token))
                    
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
                    if dataResponse.get('role', { 'name': None }):
                        user['role'] = dataResponse.get('user_role', {}).get('name', None)
                    
                    # set the organization
                    if dataResponse.get('org', { 'uid': None }):
                        user['organization'] = dataResponse.get('org',{ 'uid': None }).get('uid')
                    
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

                    # Adding JWK to the Cache
                    CACHE_TIME = TOKEN_CACHE_TIME  # one hour
                    cache.set(token, user, CACHE_TIME)

        
        return user                                                                   


        

