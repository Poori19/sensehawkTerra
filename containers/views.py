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
    def CreateOrUpdateOrgContainerAndAttachGroups(data): 
        
        dataDict = {}
        if data.get('organization', None) and data.get('container', None) and 'groups' in data:
            
            # organization Creation
            returnOrgData = OrganizationMethods.CreateOrUpdateOrg(data.get('organization'))
            if isinstance(returnOrgData,Organization):
                dataDict['org'] = returnOrgData.uid
            else:
                errorList = returnOrgData.get('error')
                errorList['org_uid'] = data.get('organization').get('uid')
                return {'error': True, 'errorList':errorList, 'data': dataDict}
            
            # creation of container 
            containerData = data.get('container')
            containerData['organization'] =  returnOrgData.pk
            returnContainerData = ContainerViewMethods.CreateorUpdateContainerView(containerData)
            
            if isinstance(returnContainerData,ContainerView):
                containerView = returnContainerData
                dataDict['containerView'] = containerView.uid
                
            elif returnContainerData.get('error', None):
                returnContainerData['error']['container_uid'] = data.get('container').get('uid')
                return {'error': True, 'errorList':returnContainerData.get('error'),'data': dataDict}
            
            # creation of groups
            groupsData = data.get('groups', None)
            groupErrorList = []; dataDict['groups'] = []; 
            projectErrorList = []; dataDict['projects'] = [] 


            for groupData in groupsData:

                eachGroupSuccessData = {'group' : None , 'projects': []}

                groupData['containerView'] = containerView.pk
                groupData['organization'] = returnOrgData.pk
                returnGroupData = OrganizationGroupMethods.CreateOrUpdateGroup(groupData)

                if isinstance(returnGroupData, OrganizationGroup):

                
                    eachGroupSuccessData['group'] = returnGroupData.pk

                    # clear all the projects
                    returnGroupData.organizationproject_set.clear()  

                    # create Project
                    projectDataDictList = groupData.get('projects', [])

                    for projectDataDict in projectDataDictList:
                        projectDataDict['group'] = returnGroupData.pk
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


     


            

        




