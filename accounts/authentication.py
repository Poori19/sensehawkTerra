from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from .middleware import OktaAuthenticationMiddleware


class UserAuthentication(authentication.BaseAuthentication):
    """
        Check if the user is active.
    """
    def authenticate(self, request):
        try:
            user = getattr(request._request, 'user', None)
            if user:
                user = user._wrapped
                if user.get('status').upper() == 'ACTIVE' :
                    return (user,None)
                else:
                    raise exceptions.AuthenticationFailed({'error': True, 'success': False, 'errorList':'user is not active'})
            else:
                raise exceptions.AuthenticationFailed({'error': True, 'success': False, 'errorList':'Invalid user'})
        except:
            raise exceptions.AuthenticationFailed({'error': True, 'success': False, 'errorList':'Request without User'})


