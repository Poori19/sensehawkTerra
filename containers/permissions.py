from rest_framework import permissions
from dependantmodels.models import OrganizationProject
from accounts.permissions import SuperUserPermission
from general.permissions import (
    SuperUserPermission,
    IsObjWriteUser, 
    IsManagerOrOwner,
    IsObjReadUser,
    IsObjOwner
)

class CanUpdateContainer(permissions.BasePermission):
    """ Check if the user has permission to create Feature """

    message = {'error': True, 'success': 'False', 'errorList': "You do not have permission to perform this action."}

    def has_object_permission(self, request, view, obj):

        if SuperUserPermission.has_permission(self, request, view):
            return True

        if IsObjOwner.has_object_permission(self, request, view, obj ):
            return True

        if IsObjWriteUser.has_object_permission(self, request, view, obj ):
            return True

        if obj.organization and IsObjWriteUser.has_object_permission(self, request, view, obj.organization ):
            return True

        if obj.organization and IsManagerOrOwner.has_object_permission(self, request, view,obj.organization.uid):
            return False
            
        return False

class CanReadContainer(permissions.BasePermission):
    """ Check if the user has permission to create Feature """

    message = {'error': True, 'success': 'False', 'errorList': "You do not have permission to perform this action."}
   
    def has_object_permission(self, request, view, obj):

       
        if SuperUserPermission.has_permission(self, request, view):
            return True

        if IsObjOwner.has_object_permission(self, request, view, obj ):
            return True

        if IsObjReadUser.has_object_permission(self, request, view, obj ):
            return True

        if obj.organization and  IsObjReadUser.has_object_permission(self, request, view, obj.organization ):
            return True
        
        if obj.organization and IsManagerOrOwner.has_object_permission(self, request, view, obj, obj.organization.uid ):
            return True

        return False







