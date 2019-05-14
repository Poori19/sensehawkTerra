from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status
from django.db.models import Q
from rest_framework import viewsets

from rest_framework.filters import (
        SearchFilter,
        OrderingFilter,
    )
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView, 
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )


from .paginators import ContainerPaginator
from .serializers import ContainerViewSerializer
from dependantmodels.serializers import OrderedListProjectGroupByGroupSerializer
from dependantmodels.utils import OrganizationMethods,OrganizationGroupMethods,OrganizationProjectMethods
from .utils import ContainerViewMethods
from accounts.permissions import SuperUserPermission
from accounts.authentication import UserAuthentication
from accounts.utils import UserClass
from dependantmodels.serializers  import OrganizationGroupSerializerProjectsPerGroup, OrganizationGroupSerializer,OrderedListProjectSerializer
from dependantmodels.models import Organization,OrganizationGroup,ContainerView, OrganizationProject
from features.models import FeatureTypeGroup,Feature
from containers.permissions import CanUpdateContainer,CanReadContainer


# Create the Container
class ContainerViewCreateAPIView(CreateAPIView):

    """  Creates the Container """
    queryset = ContainerView.objects.all()
    serializer_class = ContainerViewSerializer
    permission_classes = [CanUpdateContainer]
    authentication_classes = (UserAuthentication,)

    # def create(self, request, *args, **kwargs):
    #     """Overiding the create function"""
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class ContainerViewListAPIView(ListAPIView):
    """ 
        List all the containers of the organization  
    """
    queryset = ContainerView.objects.filter(active = True)
    serializer_class = ContainerViewSerializer
    filter_backends= [SearchFilter, OrderingFilter]
    authentication_classes = [UserAuthentication]
    permission_classes = []
    search_fields = []
    
    def get_queryset(self, *args, **kwargs):
        filters = {}
        queryset =  self.queryset.order_by('organization')
        user = self.request.user
        if UserClass.UserIsSuperUser(user):
            return queryset
        else:
            orgObjs = Organization.objects.filter(Q(uid = user.get('organization')))
            if orgObjs.exists():
                filters['organization'] = orgObjs.first()
                return self.queryset.filter(**filters)
        return ContainerView.objects.none() 

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        userUid = request.user.get('uid')

        if UserClass.UserIsSuperUser(request.user) or request.user.get('is_manager') or request.user.get('is_owner') :
            filteredQueryset = queryset
        else:
            filterDict = [{'uid': userUid}]
            filteredQueryset_1 = queryset.filter(Q(readLabels__contains = filterDict) | Q(readUsers__contains = filterDict)| Q(writeUsers__contains = filterDict) | Q(writeLabels__contains = filterDict) | Q(owner__uid = userUid))
            filteredQueryset_2 = queryset.filter(Q(organization__readLabels__contains = filterDict) | Q(organization__readUsers__contains = filterDict)| Q(organization__writeUsers__contains = filterDict) | Q(organization__writeLabels__contains = filterDict))
            filteredQueryset = filteredQueryset_1 | filteredQueryset_2
        serializer = self.get_serializer(filteredQueryset, many=True)
        return Response(serializer.data)


        
class AddFTGToContainerView(APIView):
    """
    Add FTG To the Container View
    """
    authentication_classes = [UserAuthentication]
    permission_classes = [CanUpdateContainer]

    def get(self, request,uid=None, format=None):
        return Response("Add FTG To the Container View")

    def post(self,request,uid,format=None):

        
        FTGUid = request.data.get('featureTypeGroup', None)
        try: 
            containerView = ContainerView.objects.get(uid = uid)
            # May raise a permission denied
            self.check_object_permissions(self.request, containerView)
        except ContainerView.DoesNotExist:
            return Response({'error': True,  'errorList': 'Container with uid doesnot exist'}, status = status.HTTP_404_NOT_FOUND)
        try: 
            featureTypeGroup = FeatureTypeGroup.objects.get(uid = FTGUid)
        except FeatureTypeGroup.DoesNotExist:
            return Response({'error': True, 'errorList': 'FTG with uid doesnot exist'}, status = status.HTTP_404_NOT_FOUND)
        
        if featureTypeGroup:
            if featureTypeGroup.org == containerView.organization:
                containerView.featureTypeGroups.add(featureTypeGroup)
            else:
                return Response({'error': True, 'errorList' : "feature Type group belong to differnt org"},status = status.HTTP_400_BAD_REQUEST)


        message = { 'featureTypeGroup':FTGUid,'containerView': uid }
        return Response({'success': True, 'data' : message},status = status.HTTP_200_OK)


class RemoveFTGToContainerView(APIView):
    """
    Remove FTG To the Container View
    """
    authentication_classes = [UserAuthentication]
    permission_classes = [CanUpdateContainer]

    def get(self, request,uid=None, format=None):
        return Response("Remove FTG To the Container View")

    def post(self, request,uid, format=None):

        FTGUid = request.data.get('featureTypeGroup', None)
        try: 
            containerView = ContainerView.objects.get(uid = uid)
        except ContainerView.DoesNotExist:
            return Response({'error': True, 'errorList': 'Container with uid doesnot exist', 'data':[]}, status = status.HTTP_404_NOT_FOUND)
        try: 
            featureTypeGroup = FeatureTypeGroup.objects.get(uid = FTGUid)
        except FeatureTypeGroup.DoesNotExist:
            return Response({'error': True, 'errorList': 'FTG with uid doesnot exist'}, status = status.HTTP_404_NOT_FOUND)
        
        # Remove FTG from the CV
        if featureTypeGroup:
            containerView.featureTypeGroups.remove(featureTypeGroup )
        
        # Get all the Features associated with the CV and dereference FT from them
        message = {'featureTypeGroup':FTGUid,'containerView': uid }
        featureTypes = featureTypeGroup.featureTypes.all()
        features = Feature.objects.filter(project__group__containerView = containerView,featureType__in = featureTypes)
        message['features'] = list(features.values_list('uid', flat = True))    
        features.update(featureType = None)      

        message['featureTypes'] = featureTypes.values_list('uid', flat = True)
        return Response({'success': True,'data':message},status = status.HTTP_200_OK)

class ContainerViewRetrieveAPIView(RetrieveAPIView):
    """ 
        Get the container of the organization  
    """
    queryset = ContainerView.objects.filter(active = True)
    serializer_class = ContainerViewSerializer
    authentication_classes = [UserAuthentication]
    permission_classes =[CanReadContainer]
    lookup_field = 'uid'

    def retrieve(self, request, *args, **kwargs):
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid =uid )

            # May raise a permission denied
            self.check_object_permissions(self.request, instance)

        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist' }, status= status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance)
        data = self.get_serializer(instance).data 

        # get all the active groups of the container view  
        groups = instance.organizationgroup_set.filter(active = True)     
        data['groups'] = OrganizationGroupSerializerProjectsPerGroup(groups, many = True).data
        return Response(data)

   
            
class CreateOrUpdateOrgContainerAndAttachGroupsFromJson(APIView):

    authentication_classes = [UserAuthentication]
    permission_classes = [SuperUserPermission]

    def get(self, request):
        data = {"message": "This request used to create or update containers and attach groups to the container "}
        return Response(data)

    def post(self, request):
        data = request.data
        returnData = self.CreateOrUpdateOrgContainerAndAttachGroups(data)
        return Response(returnData)

    @staticmethod
    def popDataAttributes(data):
        popKeys = [
            'read_labels',
            'read_users',
            'write_labels',
            'write_users'
        ]
        for key in popKeys:
            data.pop(key)

        return data

    @staticmethod
    def removeDuplicates(data):
        from iteration_utilities import unique_everseen  
        permissionkeys = ["readLabels", "readUsers", "writeLabels", "writeUsers"]
        for key in permissionkeys:
            if data.get(key):
                data[key] = list(unique_everseen(data.get(key)))

        return data

    @staticmethod
    def mapPermissionsBasedOnModels(data,model = None):
        from iteration_utilities import unique_everseen     
        permisionData = {}
        permKeyValues = {
            'read_labels': 'readLabels',
            'read_users': 'readUsers',
            'write_labels': 'writeLabels',
            'write_users': 'writeUsers'
        }

        for key, value in permKeyValues.items():
            if data.get(key):
                permisionData[value] = data[key]
            else:
                permisionData[value] = []

        if model in ['asset', 'entity'] and data.get('owner',None):
            permisionData['readUsers'].append(data.get('owner'))
            permisionData['writeUsers'].append(data.get('owner'))

        permisionData = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.removeDuplicates(permisionData)
        return permisionData


    @staticmethod
    def updateContainerPermissions(containerData, permissions):
        keys = ["readLabels", "readUsers", "writeLabels", "writeUsers"]
    
        containerPermissions = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.mapPermissionsBasedOnModels(containerData)
        containerData.update(containerPermissions)
        containerData = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.popDataAttributes(containerData)
        for key in keys:
            if permissions.get(key):
                if containerData.get(key):
                    containerData[key].extend(permissions.get(key))
                else:
                    containerData[key] = permissions.get(key)
        containerData = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.removeDuplicates(containerData)
        return containerData
    

    @staticmethod
    def getReadAndWriteUsersAndLabelsFromEntityAsset(data):
        permissions = {'readUsers': [], 'readLabels': [], 'writeLabels': [], 'writeUsers': []}

        # from entity
        if data.get('entity'): 
            entityPermissions = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.mapPermissionsBasedOnModels(data.get('entity'), 'entity')
            for key , value in entityPermissions.items():
                if key in permissions:
                    permissions[key].extend(value)

        if data.get('asset'): 
            assetPermissions = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.mapPermissionsBasedOnModels(data.get('asset'), 'asset')
            for key , value in assetPermissions.items():
                if key in permissions:
                    permissions[key].extend(value)

        return permissions

    @staticmethod
    def CreateOrUpdateOrgContainerAndAttachGroups(data): 

        dataDict = {}
        if data.get('organization', None) and data.get('container', None) and 'groups' in data:
        
            # organization Creation
            orgPermissions = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.mapPermissionsBasedOnModels(data.get('organization'))
            data.get('organization').update(orgPermissions)
            returnOrgData = OrganizationMethods.CreateOrUpdateOrg(data.get('organization'))
            if isinstance(returnOrgData,Organization):
                dataDict['org'] = returnOrgData.uid
            else:
                errorList = returnOrgData.get('error')
                errorList['org_uid'] = data.get('organization').get('uid')
                return {'error': True, 'errorList':errorList, 'data': dataDict}

            containerPermissions = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.getReadAndWriteUsersAndLabelsFromEntityAsset(data)
            # creation of container 
            containerData = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.updateContainerPermissions(data.get('container'), containerPermissions)
            containerData['organization'] =  returnOrgData.pk
            returnContainerData = ContainerViewMethods.CreateorUpdateContainerView(containerData)
            
            if isinstance(returnContainerData,ContainerView):
                containerView = returnContainerData
                dataDict['containerView'] = containerView.uid

                # clear all the groups
                containerView.organizationgroup_set.clear()  

            elif returnContainerData.get('error', None):
                returnContainerData['error']['container_uid'] = data.get('container').get('uid')
                return {'error': True, 'errorList':returnContainerData.get('error'),'data': dataDict}
            
            # creation of groups
            groupsData = data.get('groups', None)
            groupErrorList = []; dataDict['groups'] = []; 
            projectErrorList = []; 


            for groupData in groupsData:

                eachGroupSuccessData = {'group' : None , 'projects': []}

                groupPermissions = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.mapPermissionsBasedOnModels(groupData)
                groupData.update(groupPermissions)
                groupData = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.popDataAttributes(groupData)
                
                groupData['containerView'] = containerView.pk
                groupData['organization'] = returnOrgData.pk
                returnGroupData = OrganizationGroupMethods.CreateOrUpdateGroup(groupData)

                if isinstance(returnGroupData, OrganizationGroup):

                    eachGroupSuccessData['group'] = returnGroupData.pk

                    # clear all the projects
                    returnGroupData.organizationproject_set.all().update(active = False)    
                    returnGroupData.organizationproject_set.clear()  

                    # create Project
                    projectDataDictList = groupData.get('projects', [])

                    for projectDataDict in projectDataDictList:

                        projectPermissions = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.mapPermissionsBasedOnModels(projectDataDict)
                        projectDataDict.update(projectPermissions)
                        projectDataDict = CreateOrUpdateOrgContainerAndAttachGroupsFromJson.popDataAttributes(projectDataDict)

                        projectDataDict['group'] = returnGroupData.pk

                        if 'reports' in projectDataDict:
                            projectDataDict['data'] = projectDataDict['reports']

                        projectData = OrganizationProjectMethods.CreateOrUpdateProject(projectDataDict)
                        if not isinstance(projectData, OrganizationProject):
                            projectError = projectData.get('error')
                            projectError['project_uid'] = projectDataDict.get('uid')
                            projectErrorList.append(projectError)
                        else:
                            eachGroupSuccessData['projects'].append(projectData.uid)
                    
                    dataDict['groups'].append(eachGroupSuccessData)
                
                elif returnGroupData.get('error'):
                    returnGroupData['error']['group_uid'] = groupData.get('uid')
                    groupErrorList.append(returnGroupData.get('error'))

            
            if groupErrorList or projectErrorList:
                errorList = {}
                errorList['groups'] = groupErrorList
                errorList['projects'] =  projectErrorList
                return {'error': True, 'errorList':errorList, 'data': dataDict}
            else:
                return {'error': False, 'success' : True, 'data': dataDict, 'errorList': []}
        else:
            return {'error' : True, 'errorList': 'The Json doesnot contain either of the attributes "organization,container,groups" '}


     


            

        




