from rest_framework import permissions
from dependantmodels.models import OrganizationProject,ContainerView
from accounts.permissions import SuperUserPermission
from general.permissions import (
    SuperUserPermission,
    IsObjWriteUser, 
    IsManagerOrOwner,
    IsObjReadUser
)

class CanCreateFeature(permissions.BasePermission):
    """ Check if the user has permission to create Feature """

    message = {'error': True, 'success': 'False', 'errorList': "you don't have permission to create model feature"}

    def has_permission(self, request, view):
        
        projectUid = request.parser_context.get('kwargs').get('project_uid', None)

        if SuperUserPermission.has_permission(self, request, view):
            return True

        containerViewUid = OrganizationProject.objects.filter(uid = projectUid).values_list('group__containerView', flat = True)   
        
        if containerViewUid and containerViewUid[0]:

            containerView = ContainerView.objects.get(uid = containerViewUid[0])    

            if IsObjWriteUser.has_object_permission(self, request, view, containerView ):
                return True

            if containerView.organization and IsObjWriteUser.has_object_permission(self, request, view, containerView.organization ):
                return True
                    
            if containerView.organization and IsManagerOrOwner.has_object_permission(self, request, view,containerView, containerView.organization.uid):
                return True

        return False


class CanUpdateFeature(permissions.BasePermission):
    """ Check if user has permission to update the Feature """  
    
    message = {'error': True, 'success': 'False', 'errorList': "you don't have permission to model feature"}
    def has_object_permission(self, request, view, obj):

        
        if SuperUserPermission.has_permission(self, request, view):
            return True

        if obj and obj.project and obj.project.group and obj.project.group.containerView:  

            containerView= obj.project.group.containerView
            
            if IsObjWriteUser.has_object_permission(self, request, view, containerView ):
                return True

            if containerView.organization and IsObjWriteUser.has_object_permission(self, request, view, containerView.organization ):
                return True
                    
            if containerView.organization and IsManagerOrOwner.has_object_permission(self, request, view,containerView, containerView.organization.uid):
                return True

        return False

class CanReadFeature(permissions.BasePermission):
    """ Check if user has permission to update the Feature """  
    
    message = {'error': True, 'success': 'False', 'errorList': "you don't have permission to model feature"}
    def has_object_permission(self, request, view, obj):
        
        if SuperUserPermission.has_permission(self, request, view):
            return True

        if obj and obj.project and obj.project.group and obj.project.group.containerView:  

            containerView = obj.project.group.containerView
            
            if IsObjReadUser.has_object_permission(self, request, view, containerView ):
                return True

            if containerView.organization and IsObjReadUser.has_object_permission(self, request, view, containerView.organization ):
                return True
                    
            if containerView.organization and IsManagerOrOwner.has_object_permission(self, request, view,containerView, containerView.organization.uid):
                return True
                
        return False