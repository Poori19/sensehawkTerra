from rest_framework import permissions
from .utils import  (
    checkUserHasWritePermission,
    checkUserHasReadPermission,
    checkUserIsOwner
)
from accounts.constants import SUPER_USER_ROLES


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

class IsManagerOrOwner(permissions.BasePermission):
    """
        Check if the user is manager or owner
    """

    def has_permission(self, request, view):
        user = request.user
        if type(user) == dict:
            if (user.get('is_owner',False) or user.get('is_manager',False)) and user.get('organization') :
                return True
        return False

    def has_object_permission(self, request, view, obj, organizationUid=None):
        #Instance must have an attribute named `owner`.

        user = request.user
        if type(user) == dict:
            if (user.get('is_owner',False) or user.get('is_manager',False)) and user.get('organization') :
                # Check they belong to same organization
                if user.get('organization') == organizationUid:
                    return True
        return False


class IsObjReadUser(permissions.BasePermission):
    """
        Check if the user is in the Read User Permissions
    """
    def has_object_permission(self, request, view, obj):

        #import pdb;pdb.set_trace()
    
        #Instance must have an attribute named `owner`.
        user = request.user
        if checkUserHasReadPermission(obj,user):
            return True 
        return False


class IsObjWriteUser(permissions.BasePermission):
    """
        Check if the user is in the Write User Permissions
    """

    def has_object_permission(self, request, view, obj):
        
        user = request.user

        # Instance must have an attribute named `owner`.
        if  checkUserHasWritePermission(obj,user):
            return True 
        return False

