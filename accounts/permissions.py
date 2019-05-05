from rest_framework import permissions
import environ
env = environ.Env()
import json

from .constants import SUPER_USER_ROLES

class SuperUserPermission(permissions.BasePermission):
    """
    Check if the user has role of superUser 
    """
    message = {'error': True, 'success': 'False', 'errorList': "You do not have permission to perform this action."}

    def has_permission(self, request, view):
        
        user = getattr(request._request, 'user', None)
        if type(user) == dict and user.get('role'):
            if type(user['role']) == str and user.get('role') and user['role'] in SUPER_USER_ROLES:
                return True
            if type(user['role']) == list:
                for role in user['role']:
                    if role in SUPER_USER_ROLES:
                        return True
        return False
