from django.shortcuts import render
from rest_framework.decorators import api_view

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
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
from rest_framework import status
from .models import Organization,OrganizationGroup,OrganizationProject
from .utils import OrganizationMethods,OrganizationGroupMethods,OrganizationProjectMethods
from .serializers import (
    OrganizationSerializer,
    OrganizationGroupSerializer,
    OrganizationProjectSerializer,
    OrderedListProjectGroupByGroupSerializer,
    OrganizationGroupCreateUpdateSerializer,
    OrganizationCreateUpdateSerializer
)
from accounts.authentication import UserAuthentication
from accounts.utils import UserClass
from .paginators import ProjectPaginator


class CreateOrgGroupProjectFromJson(APIView):

    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self, request):
        data = {"message": "This request used to create or update the models 'Org', 'Project' and 'Group' "}
        return Response(data)

    def post(self, request):
        returnData = self.CreateOrgGroupProject(request.data)
        if returnData.get('error'):
            return Response(returnData, status= status.HTTP_403_FORBIDDEN)
        elif returnData.get('success'):
            return Response(returnData, status= status.HTTP_200_OK)


    @staticmethod
    def CreateOrgGroupProject(data):
        returnData = {'success': False, 'error': False,'data':{}, 'errorlist': []}
        errorList = {}
        orgDict = data.get('organization', {})
        orgData = OrganizationMethods.CreateOrUpdateOrg(orgDict)
        if isinstance(orgData, Organization):
            returnData['data']['org'] = orgData.pk
            returnData['data']['groups'] = []
            returnData['data']['projects'] = []
            groupKeys =  ['uid','name', 'description', 'active', 'owner', 'readUsers', 'writeUsers', 'readLabels', 'writeLabels' ]
            if 'groups' in data:
                groups = data['groups']
                for eachGroup in groups:
                    groupDict = {}
                    for key in groupKeys:
                        if key in eachGroup:
                            groupDict[key] = eachGroup[key]

                    groupDict['organization'] = orgData.pk
                    groupData = OrganizationGroupMethods.CreateOrUpdateGroup(groupDict)

                    if isinstance(groupData, OrganizationGroup):
                        returnData['data']['groups'].append(groupData.pk)
                        if eachGroup.get('projects'):
                            for eachProject in eachGroup.get('projects', []):
                                eachProject['group'] = groupData.pk
                                projectData = OrganizationProjectMethods.CreateOrUpdateProject(eachProject)
                                if not isinstance(projectData, OrganizationProject):
                                    errorList['project'] = projectData
                                else:
                                    returnData['data']['projects'].append(projectData.pk)
                    else:
                        errorList['group'] = groupData
        else:
            errorList['org'] = orgData

        if errorList:
            returnData['errorlist'] = errorList
            returnData['error'] = True
        else:
            returnData['success'] = True
        
        return returnData



class GetAllProjectsUserHasAccess(APIView):

    authentication_classes = [UserAuthentication]
    permission_classes = []

    def get(self, request):

        user = request.user
        org = Organization.objects.filter(Q(uid = user['organization']) | Q(name =user['organization']))
        if  org.exists():
            # User is_manager and is_owner
            if UserClass.UserIsManagerOrIsOwner(user):
                projects = OrganizationProject.objects.filter(group__organization__in = org )
                serializers = OrderedListProjectGroupByGroupSerializer(projects,many = True )
                return Response(serializers.data,status = status.HTTP_200_OK )

            # get the Groups for which the user has acess
            groupsUids = OrganizationGroupMethods.GetGroupUidsUserHasWritePermission(user,org)

            # get the projects for which the user has acess
            projectUids = OrganizationProjectMethods.GetProjectUidsUserHasWritePermission(user,org)

            projects = OrganizationProject.objects.filter(Q(group__uid__in = groupsUids) | Q(uid__in =projectUids) )
            serializers = OrderedListProjectGroupByGroupSerializer(projects,many = True )
            return Response(serializers.data,status = status.HTTP_200_OK )

            # paginator = CustomPaginator()
            # response = paginator.generate_response(tables, ViewTableSerializer, request)
            # return response

        return Response("organization doesnot exist",status = status.HTTP_400_BAD_REQUEST )

    
class OrganizationProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for the model Project
    """
    queryset = OrganizationProject.objects.all()
    serializer_class = OrganizationProjectSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = []
    #authentication_classes = []
    pagination_class = ProjectPaginator
    lookup_field = 'uid'

    def get_queryset(self, *args, **kwargs):
        queryset = self.queryset
        user = self.request.user
        defaultFilters = {"active" : True}
        if 'organization' in user and user['organization']: 
            org = Organization.objects.filter((Q(name= user['organization'])| Q(uid = user['organization'])))
            if org.exists():
                return queryset.filter(**defaultFilters).filter( Q(group__organization = org))
            else:
                return []
        return queryset.filter(**defaultFilters)
    


# Create the OrganizationGroup 
class OrganizationGroupCreateAPIView(CreateAPIView):    
    """  Creates the Organization Group """
    queryset = OrganizationGroup.objects.all()
    serializer_class = OrganizationGroupCreateUpdateSerializer
    #permission_classes = [CanCreateViewTable]
    permission_classes = []
    authentication_classes = (UserAuthentication,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# Create the OrganizationGroup 
class OrganizationCreateAPIView(CreateAPIView):    
    """  Creates the Organization Group """
    queryset = Organization.objects.all()
    serializer_class = OrganizationCreateUpdateSerializer
    #permission_classes = [CanCreateViewTable]
    permission_classes = []
    authentication_classes = (UserAuthentication,)


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

