from rest_framework import permissions
from dependantmodels.models import OrganizationProject,ContainerView
from accounts.permissions import SuperUserPermission
from general.permissions import (
    SuperUserPermission,
    IsObjWriteUser, 
    IsManagerOrOwner,
    IsObjReadUser
)

class CanCreateUpdateFeature(permissions.BasePermission):
    """ Check if the user has permission to create Feature """

    message = {'error': True, 'success': 'False', 'errorList': "you don't have permission to create model feature"}

    def has_permission(self, request, view):

        import pdb;pdb.set_trace()
        
        projectUid = None

        if SuperUserPermission.has_permission(self, request, view):
            return True

        if request.data.get('properties',{}): 
            if request.data.get('properties',{}).get('project',None):
                projectUid  = request.data.get('properties',{}).get('project')

            containerViewUid = OrganizationProject.objects.filter(uid = projectUid).values_list('group__containerView', flat = True)   
            if containerViewUid:
                containerView = ContainerView.objects.get(uid = containerViewUid[0])    
                return (
                        IsObjWriteUser.has_object_permission(self, request, view, containerView ) or
                        IsObjWriteUser.has_object_permission(self, request, view, containerView.organization ) or
                        IsManagerOrOwner.has_permission(self, request, view,containerView.organization.uid)
                )
        
        return False


# class CanUpdateFeature(permissions.BasePermission):
#     """ Check if user has permission to update the Feature """  
    
#     message = {'error': True, 'success': 'False', 'errorList': "you don't have permission to model feature"}
#     def has_object_permission(self, request, view, obj):

#         if SuperUserPermission.has_permission(self, request, view):
#             return True

#         if obj and obj.project and obj.project.group and obj.project.group.containerView:  
#             return (
#                 isObjWriteUser.has_object_permission(self, request, view, obj.project.group.containerView ) 
#         )
#         return False

class CanReadFeature(permissions.BasePermission):
    """ Check if user has permission to update the Feature """  
    
    message = {'error': True, 'success': 'False', 'errorList': "you don't have permission to model feature"}
    def has_object_permission(self, request, view, obj):
        
        if SuperUserPermission.has_permission(self, request, view):
            return True

        if obj and obj.project and obj.project.group and obj.project.group.containerView:  
                if IsObjReadUser.has_object_permission(self,request, view, obj.project.group.containerView)  :
                    return True

                if obj.project.group.containerView.organization:
                    return(
                    IsObjReadUser.has_object_permission(self,request, view, obj.project.group.containerView.organization) or
                    IsManagerOrOwner.has_object_permission(self, request, view, obj.project.group.organization.uid)
                    )
        return False