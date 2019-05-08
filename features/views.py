from django.shortcuts import render
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import action

from django.http import Http404

from django.db.models import Q
from rest_framework import viewsets

from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
    )

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
from django.http import Http404


from accounts.authentication import UserAuthentication
from accounts.permissions import SuperUserPermission
from .models import Feature, FeatureType, FeatureTypeGroup
from .serializers import (
    FeatureTypeSerializer,
    FeatureSerializer,
    FeatureTypeCreateUpdateSerializer,
    FeatureCreateUpdateSerializer,
    FeatureTypeGroupSerializer,
    FeatureTypeGroupCustomSerializer,
    OrderedListFTByFTG
    )

from .paginators import FeaturePaginator
from dependantmodels.models import Organization,OrganizationProject,ContainerView

from .paginators import FeaturePaginator
from accounts.utils import RandomStringGenerator,UserClass
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import CanCreateFeature,CanReadFeature,CanUpdateFeature,CanListFeature
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination # Any other type works as well
from general.permissions import BlockPermission

class FeatureViewSet(viewsets.ModelViewSet):
    """
    A viewset for model 'FeatureType'
    """
    queryset = Feature.objects.filter(active = True,project__active = True)
    serializer_class = FeatureCreateUpdateSerializer
    authentication_classes = [UserAuthentication]
    lookup_field = 'uid'
    permission_classes = []
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('project',)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):

        if self.action in ['featureCreateAndList']  and  self.request.method == 'POST':
            return FeatureCreateUpdateSerializer

        if self.action in ['update']:
            return FeatureCreateUpdateSerializer

        if self.action in ['featureCreateAndList', 'featuresGroupByGroup']  and  self.request.method == 'GET':
            return FeatureSerializer
        return FeatureSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes  = []
        if self.action in ['featureCreateAndList']  and  self.request.method == 'POST':
            permission_classes = [CanCreateFeature]

        if self.action in ['featureCreateAndList', 'featuresGroupByGroup']  and  self.request.method == 'GET':
            permission_classes = [CanListFeature]

        if self.action in ['create']:
            permission_classes = [BlockPermission]

        elif self.action in ['retrieve']:
            permission_classes = [CanReadFeature]

        elif self.action in ['update', 'destroy']:
            permission_classes = [CanUpdateFeature]
            
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):

        queryset = self.queryset
        user = self.request.user

        if UserClass.UserIsSuperUser(user):
            return queryset.order_by('project')
        else:
            return queryset.filter(Q(project__group__organization__uid = user['organization']) | Q(owner__uid = user['uid']))
        return queryset

    # def list(self, request, *args, **kwargs):
    #     import pdb;pdb.set_trace()
    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
       
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid =uid )
            # May raise a permission denied
            self.check_object_permissions(self.request, instance)
        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist'}, status= status.HTTP_404_NOT_FOUND)
        
        if request.data.get('properties', {'featureType': None}).get('featureType'):
            featureTypes = FeatureType.objects.filter(uid = request.data.get('properties').get('featureType'))
            if featureTypes.exists():
                request.data['properties']['featureType'] = featureTypes.first().pk
            else:
                return Response({'error': True, 'errorList': 'feature type with uid doesnot exist'}, status= status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data,status = status.HTTP_200_OK)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
                                                                   
        return Response({'error': True, 'errorList':serializer.errors },status = status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, *args, **kwargs):

        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid =uid )

            # May raise a permission denied
            self.check_object_permissions(self.request, instance)

        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist'}, status= status.HTTP_404_NOT_FOUND)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.active = False
        instance.save()

    def retrieve(self, request, *args, **kwargs):
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid =uid )

            # May raise a permission denied
            self.check_object_permissions(self.request, instance)

        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist'}, status= status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(methods=['get'], detail=True,renderer_classes=[JSONRenderer],url_path='master', authentication_classes = [UserAuthentication])
    def hierarchyFeatures(self, request, *args, **kwargs):
        data = []
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(**kwargs )
        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist'}, status= status.HTTP_404_NOT_FOUND)

        features =  self.get_queryset().filter(Q(hierarchyProperties__master_uid = instance.uid)  | Q(uid = instance.uid)).distinct()
        if features.exists():
            serializer = self.get_serializer(features, many = True)
        return Response(serializer.data, status= status.HTTP_200_OK)

    # @action(methods=['get'], detail=False,renderer_classes=[JSONRenderer], url_name='featuresGroupByProject', url_path='project/(?P<project_uid>[^/.]+)',    authentication_classes = [UserAuthentication])
    # def featuresGroupByProject(self, request, *args, **kwargs):
    #     features = []
    #     if kwargs.get("project_uid"):  
    #         filters = {'project__uid': kwargs.get("project_uid")} 
    #         features = self.get_queryset().filter(**filters)
    #     serializer = self.get_serializer(features, many = True)
    #     return Response(serializer.data, status= status.HTTP_200_OK)

    @action(methods=['get'], detail=False,renderer_classes=[JSONRenderer],url_name='featuresGroupByGroup', url_path='group/(?P<group_uid>[^/.]+)')
    def featuresGroupByGroup(self, request, *args, **kwargs):
        features = []
        if kwargs.get("group_uid"):  
            filters = {'project__group__uid': kwargs.get("group_uid")} 
            features = self.get_queryset().filter(**filters)
        serializer = self.get_serializer(features, many = True)
        return Response(serializer.data, status= status.HTTP_200_OK)

    @action(methods=['post', 'get'], detail=False,renderer_classes=[JSONRenderer], url_name='create project', url_path='project/(?P<project_uid>[^/.]+)', authentication_classes = [UserAuthentication])
    def featureCreateAndList(self, request, *args, **kwargs):
        """ Overiding the create function """

        if request.method == 'GET':
            features = []
            if kwargs.get("project_uid"):  
                filters = {'project__uid': kwargs.get("project_uid"), 'project__active': True} 
                features = self.get_queryset().filter(**filters)
            serializer = self.get_serializer(features, many = True)
            return Response(serializer.data, status= status.HTTP_200_OK)

        if request.method == 'POST':
            returnFormat = {'error': False, 'success': False, 'data': {}, 'errorList': {}} 

            projectUid = kwargs.get('project_uid')
            try:
                project = OrganizationProject.objects.get(uid = projectUid,active = True)
            except OrganizationProject.DoesNotExist:
                return Response({'error': True, 'errorList': 'project with this uid doesnot exist'}, status = status.HTTP_404_NOT_FOUND)

            # Bulk create
            
            if request.data.get('type', {}) and (request.data.get('type') == "FeatureCollection"):
                features = request.data.get('features', [])
            
                for index,feature in enumerate(features):
                    errorData = []
                    if feature.get('properties', {}):
                        if feature.get("properties", {}).get("featureType", None):
                            featureTypeUid = feature.get('properties').get('featureType')
                            featureTypes = FeatureType.objects.filter(uid = featureTypeUid )
                            if featureTypes.exists():
                                feature['properties']['featureType'] = featureTypes.first().pk
                            else:
                                errorData.append("featureType with this uid doesnot exist")
                        # lse:
                        #    errorData.append("featureType uid is not provided")

                        # if feature.get("properties", {}).get("project", None):
                        #     projectUid  = feature.get('properties').get('project')
                        #     projects = OrganizationProject.objects.filter(uid = projectUid)
                        #     if not projects.exists():
                        #         errorData.append("project with uid doesnot exist")
                        #     else:
                        #         feature['properties']['project'] = projects.first().pk
                        # else:
                        #     errorData.append("project uid is not provided")

                        feature['properties']['project'] = project.pk
                    else:
                        errorData.append("features doenot contain the attribute properties")

                    if not errorData:
                        serializer = self.get_serializer(data=feature)
                        if serializer.is_valid():
                            featureObj = self.perform_create(serializer)
                            returnFormat['data'][index] = featureObj.uid
                        else:
                            returnFormat['error'] = True
                            returnFormat['errorList'][index] = serializer.errors
                    else:
                        returnFormat['error'] = True
                        returnFormat['errorList'][index] = errorData
                
                if not returnFormat['error']:
                    returnFormat['success'] = True
            
            elif request.data.get('type', {}) and (request.data.get('type') == "Feature") and request.data.get('properties', {}):
                errorData = []

                if request.data.get("properties").get("featureType", None):
                    featureTypeUid = request.data.get('properties').get('featureType')
                    featureTypes = FeatureType.objects.filter(uid = featureTypeUid )
                    if featureTypes.exists():
                        request.data['properties']['featureType'] = featureTypes.first().pk
                    else:
                        errorData.append("featureType with this uid doesnot exist")
                # else:
                #     errorData.append("featureType uid is not provided")

                # if request.data.get("properties", {}).get("project", None):
                #     projectUid  = request.data.get('properties').get('project')
                #     projects = OrganizationProject.objects.filter(uid = projectUid)
                #     if projects.exists():
                #         request.data['properties']['project'] = projects.first().pk
                #     else:
                #         errorData.append("project with uid doesnot exist")
                # else:
                #     errorData.append("project uid is not provided")

                request.data['properties']['project'] = project.pk
                
                if not errorData:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        featureObj = self.perform_create(serializer)
                        headers = self.get_success_headers(serializer.data)
                        returnFormat['success'] =True
                        returnFormat['data'] = [featureObj.uid]
                        return Response(returnFormat, status=status.HTTP_201_CREATED, headers=headers)
                    else:
                        errorData.append(serializer.errors)
                        returnFormat['error'] = True
                        returnFormat['errorList'] = errorData
                else:
                    returnFormat['error'] = True
                    returnFormat['errorList'] = errorData
                    
            else:
                returnFormat['error'] = True
                returnFormat['errorList'] = "Incorrect Geo Json Format"

            return Response(returnFormat)


# class GetAllFeaturesConnectedToMasterFeature(RetrieveAPIView):

#     queryset = Feature.objects.all()
#     serializer_class = FeatureSerializer
#     authentication_classes = [UserAuthentication]
#     permission_classes = [CanReadFeature]
#     lookup_field = 'uid'CanUpdateFeature
#     pagination_class = FCanUpdateFeature


#     def retrieve(self, rCanUpdateFeature:

#         data = []
#         try:
#             uid = kwargs.get('uid', None)
#             instance = self.get_queryset().get(**kwargs )
#         except self.get_queryset().model.DoesNotExist:
#             return Response({'error': True, 'errorList': 'object wit uid doesnot exist' ,'success': False, 'data': []}, status= status.HTTP_404_NOT_FOUND)

#         features =  self.get_queryset().filter(Q(hierarchyProperties = {'master_uid' : instance.uid})  | Q(uid = instance.uid)).distinct()
#         if features.exists():
#             serializer = self.get_serializer(features, many = True)
#             data = serializer.data
#         return Response({'error': False, 'success': True, 'data': data}, status= status.HTTP_200_OK)


class FeatureTypeViewSet(viewsets.ModelViewSet):
    """
    A viewset for model 'FeatureType'
    """
    queryset = FeatureType.objects.filter(active = True)
    serializer_class = FeatureTypeSerializer
    authentication_classes = [UserAuthentication]
    lookup_field = 'uid'


    def get_serializer_class(self):
        if self.action == 'list':
            return OrderedListFTByFTG
        return FeatureTypeSerializer

    def get_queryset(self, *args, **kwargs):

        queryset = self.queryset
        user = self.request.user

        if UserClass.UserIsSuperUser(user):
            return queryset.order_by('org')
        else:
            return queryset.filter(Q(org__uid = user['organization']) | Q(owner__uid = user['uid']))

        # if 'organization' in user and user['organization']: 
        #     org = Organization.objects.filter((Q(name= user['organization'])| Q(uid = user['organization'])))
        #     if org.exists():
        #         return queryset.filter((Q(active = True)) & (Q(org= org) | Q(org= None)))
        
        # return queryset.filter(active = True)
        return queryset


    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)

    def create(self, request, *args, **kwargs):
        returnFormat = {'error': False, 'success' : False, 'errorList': [], 'data': []}

        if not UserClass.UserIsSuperUser(request.user) and not request.data.get('org') and request.user.get('organization'):
            request.data['org'] = request.user.get('organization')
        elif not UserClass.UserIsSuperUser(request.user) and not(request.data.get('org') == request.user.get('organization')):
            return Response({'error': True, 'success': False, 'errorList': "associating featuretypegroup with different organization", 'data': []}, status= status.HTTP_400_BAD_REQUEST)

        if request.data.get('featureTypeGroup'):
            ftg = FeatureTypeGroup.objects.filter(uid = request.data.get('featureTypeGroup'))
            if ftg.exists():
                ftgObj = ftg.first()
                request.data['featureTypeGroup'] = ftgObj.pk
            else:
                returnFormat['error'] = True
                returnFormat['errorList'] = "Feature Type Group not found with uid"
                return Response(returnFormat, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
        else:
            returnFormat['error'] = True
            returnFormat['errorList'] = serializer.errors
            return Response(returnFormat, status=status.HTTP_400_BAD_REQUEST)
            
        returnFormat['success'] = True
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        returnFormat = {'error': False, 'success': True , 'errorList': [], 'data': []}
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid =uid )
        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist' ,'success': False, 'data': []}, status= status.HTTP_404_NOT_FOUND)
    
        serializer = self.get_serializer(instance)
        returnFormat['data'] = serializer.data
        return Response(returnFormat, status= status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        returnFormat = {'error': False, 'success': True , 'errorList': [], 'data': []}
        partial = kwargs.pop('partial', False)
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid = uid )
        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist' ,'success': False, 'data': []}, status= status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        returnFormat['data'] = serializer.data
        return Response(returnFormat,status= status.HTTP_200_OK)

    # def list(self, request, *args, **kwargs):

    #     returnFormat = {'error': False, 'success': True , 'errorList': [], 'data': []}
    #     queryset = self.filter_queryset(self.get_queryset())
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     returnFormat['data'] = serializer.data
    #     return Response(returnFormat,status= status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid = uid )
            self.perform_destroy(instance)
        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist' ,'success': False, 'data': []}, status= status.HTTP_404_NOT_FOUND)
        return Response({'success': True},status=status.HTTP_204_NO_CONTENT)

    # def get_serializer_class(self):
    #     if self.action in ['create', 'update', 'partial_update']:
    #         return FeatureTypeCreateUpdateSerializer
    #     return self.serializer_class

    

class FeatureTypeGroupViewSet(viewsets.ModelViewSet):
    """
    A viewset for model 'FeatureTypeGroup'
    """
    queryset = FeatureTypeGroup.objects.filter(active = True)
    serializer_class = FeatureTypeGroupSerializer
    authentication_classes = [UserAuthentication]
    lookup_field = 'uid'


    @action(methods=['get'], detail=False,renderer_classes=[JSONRenderer], permission_classes=[],url_path='features-types')
    def featuresTypes(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        data = FeatureTypeGroupCustomSerializer(queryset, many = True).data
        return Response({"success": True, "data" :data },status = status.HTTP_200_OK )
    
    def list(self, request, *args, **kwargs):
        
        containerUid = self.request.query_params.get('container', None)
        queryset = self.filter_queryset(self.get_queryset())
        if containerUid:
            cvs = ContainerView.objects.filter(uid = containerUid)
            if cvs.exists():
                cv = cvs.first()
                ftgUids = cv.featureTypeGroups.all().values_list('uid', flat = True)
                queryset_test = queryset.filter(uid__in = ftgUids)
                queryset = queryset_test
                
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status = status.HTTP_200_OK)

    def get_queryset(self, *args, **kwargs):

        queryset = self.queryset
        user = self.request.user

        if UserClass.UserIsSuperUser(user):
            return queryset.order_by('org')
        else:
            return queryset.filter(Q(org__uid = user['organization']) | Q(owner__uid = user['uid']))


    def perform_create(self, serializer):
        return serializer.save(owner = self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Creates the FeatureTypeGroup and Connect the FeatureTypeGroup to FeatureType
        """
        featureTypes = []
        returnFormat = {'error': False, 'success': False, 'errorList': [], 'data': []}

        if not UserClass.UserIsSuperUser(request.user) and not request.data.get('org') and request.user.get('organization'):
            request.data['org'] = request.user.get('organization')
        elif not UserClass.UserIsSuperUser(request.user) and not(request.data.get('org') == request.user.get('organization')):
            return Response({'error': True, 'success': False, 'errorList': "associating featuretypegroup with diffrenet organization", 'data': []}, status= status.HTTP_400_BAD_REQUEST)

        if request.data.get('featureTypes'): 
            featureTypes = FeatureType.objects.filter(uid__in = request.data.get('featureTypes'))
            if not featureTypes.count() == len(request.data.get('featureTypes')):
                return Response({'error': True, 'success': False, 'errorList': "FeaturesTypes either of them doesnot exist", 'data': []}, status= status.HTTP_404_NOT_FOUND)
       
        # create the FTG
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            if featureTypes:
                featureTypes.update(featureTypeGroup = instance)
            returnFormat['data'] = self.get_serializer(instance).data
            returnFormat['success'] = True
            return Response(returnFormat, status=status.HTTP_201_CREATED, headers=headers)
        else:
            returnFormat['error']= True
            returnFormat['errorList'] = serializer.errors
        return Response(returnFormat,status=status.HTTP_400_BAD_REQUEST )

    def update(self, request, *args, **kwargs):
        """
        Updates the FeatureTypeGroup and update the FeatureTypeGroup in model FeatureType
        """

        featureTypes= []
        partial = kwargs.pop('partial', False)
        
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid = uid )
        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist' ,'success': False, 'data': []}, status= status.HTTP_404_NOT_FOUND)
    
        # updating the FTG
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            returnFormat = {}
            returnFormat['success'] = True
            returnFormat['data'] = self.get_serializer(instance).data
            return Response(returnFormat, status = status.HTTP_200_OK)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response({'error': True, 'errorList': serializer.errors}, status= status.HTTP_400_BAD_REQUEST)
  
    def destroy(self, request, *args, **kwargs):
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid = uid )
            FeatureType.objects.filter(featureTypeGroup = instance).delete()
            self.perform_destroy(instance)
        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist'}, status= status.HTTP_404_NOT_FOUND)
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)


