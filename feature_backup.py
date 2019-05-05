# Create the DataTable
class FeatureCreateAPIView(CreateAPIView):
    """ Creates the Features """
    queryset = Feature.objects.all()
    serializer_class = FeatureCreateUpdateSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = [CanCreateFeature]
    parser_classes = (JSONParser,)

    def create(self, request, *args, **kwargs):
        """ Overiding the create function """

        errorData = []
        returnFormat = {'error': False, 'success': False, 'data': [], 'errorList': []} 
        if request.data.get('properties', {}):
            
            if request.data.get("properties", {}).get("featureType", None):
                featureTypeUid = request.data.get('properties').get('featureType')
                featureTypes = FeatureType.objects.filter(uid = featureTypeUid )
                if featureTypes.exists():
                    request.data['properties']['featureType'] = featureTypes.first().pk
                else:
                    errorData.append("featureType with this uid doesnot exist")
            else:
                errorData.append("featureType uid is not provided")

            if request.data.get("properties", {}).get("project", None):
                projectUid  = request.data.get('properties').get('project')
                projects = OrganizationProject.objects.filter(uid = projectUid)
                if not projects.exists():
                    request.data['properties']['project'] = projects.first().pk
                    errorData.append("project with uid doesnot exist")
            else:
                errorData.append("project uid is not provided")
        else:
            errorData.append("Incorrect geo json format")

        if not errorData:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                returnFormat['success'] =True
                returnFormat['data'] = serializer.data
                return Response(returnFormat, status=status.HTTP_201_CREATED, headers=headers)
            else:
                errorData.append(serializer.errors)

        returnFormat['error'] = True
        returnFormat['errorList'] = errorData
        return Response(returnFormat, status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        #serializer.save(owner=self.request.user)
        serializer.save()


class FeatureBulkCreateAPIView(CreateAPIView):
    """ Creates the Features In Bulk """
    serializer_class = FeatureCreateUpdateSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = [CanCreateFeature]
    parser_classes = (JSONParser,)

    def create(self, request, *args, **kwargs):
        """ Overiding the create function """

        returnFormat = {'error': False, 'success': False, 'data': {}, 'errorList': {}} 

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
                    # else:
                    #     errorData.append("featureType uid is not provided")

                    if feature.get("properties", {}).get("project", None):
                        projectUid  = feature.get('properties').get('project')
                        projects = OrganizationProject.objects.filter(uid = projectUid)
                        if not projects.exists():
                            errorData.append("project with uid doesnot exist")
                        else:
                            feature['properties']['project'] = projects.first().pk
                    else:
                        errorData.append("project uid is not provided")
                else:
                    errorData.append("features doenot contain the attribute properties")

                if not errorData:
                    serializer = self.get_serializer(data=feature)
                    if serializer.is_valid():
                        featureObj = self.perform_create(serializer)
                        returnFormat['data'][index] = featureObj.uid
                    else:
                        errorData.append(serializer.errors)
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

            if request.data.get("properties", {}).get("project", None):
                projectUid  = request.data.get('properties').get('project')
                projects = OrganizationProject.objects.filter(uid = projectUid)
                if not projects.exists():
                    request.data['properties']['project'] = projects.first().pk
                    errorData.append("project with uid doesnot exist")
                else:
                    errorData.append("project uid is not provided")
            
            if not errorData:
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid():
                    featureObj = self.perform_create(serializer)
                    headers = self.get_success_headers(serializer.data)
                    returnFormat['success'] =True
                    returnFormat['data'] = featureObj.uid
                    return Response(returnFormat, status=status.HTTP_201_CREATED, headers=headers)
                else:
                    errorData.append(serializer.errors)
                    returnFormat['error'] = True
                    returnFormat['errorList'] = errorData

        else:
            returnFormat['error'] = True
            returnFormat['errorList'] = "Incorrect Geo Json Format"

        return Response(returnFormat)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    
class FeatureListAPIView(ListAPIView):
    """ List the Feature Table """
    serializer_class = FeatureCreateUpdateSerializer
    filter_backends= [SearchFilter, OrderingFilter]
    permission_classes = []
    authentication_classes = [UserAuthentication]
    search_fields = []
    pagination_class = FeaturePaginator

    def get_queryset(self, *args, **kwargs):
        return Feature.objects.filter(active = True)

class FeatureListPerProjectAPIView(ListAPIView):
    """ List the Feature Table """
    serializer_class = FeatureCreateUpdateSerializer
    filter_backends= [SearchFilter, OrderingFilter]
    permission_classes = []
    authentication_classes = [UserAuthentication]
    search_fields = []
    pagination_class = FeaturePaginator

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('uid', 'featureType__uid')

    def get_queryset(self, *args, **kwargs):
        filters = {}

        if 'project_uid' in self.kwargs:
            filters['project__uid'] = self.kwargs['project_uid']

        return Feature.objects.filter(active = True).filter(**filters)

class FeatureListPerGroupAPIView(ListAPIView):
    """ List the Feature Table """
    serializer_class = FeatureCreateUpdateSerializer
    filter_backends= [SearchFilter, OrderingFilter]
    permission_classes = []
    authentication_classes = [UserAuthentication]
    search_fields = []
    pagination_class = FeaturePaginator

    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('uid', 'featureType__uid')

    def get_queryset(self, *args, **kwargs):
        filters = {}

        if 'group_uid' in self.kwargs:
            filters['project__group__uid'] = self.kwargs['group_uid']

        return Feature.objects.filter(active = True).filter(**filters)

        
class FeatureUpdateAPIView(UpdateAPIView):
    """ List the Feature Table """
    queryset = Feature.objects.all()
    serializer_class = FeatureCreateUpdateSerializer
    authentication_classes = [UserAuthentication]
    permission_classes = [CanReadFeature]
    lookup_field = 'uid'

    def update(self, request, *args, **kwargs):
        import pdb;pdb.pdb.set_trace()

        returnFormat = {'error': False, 'success': False, 'data': {}, 'errorList': []}
        errorData = []
        partial = kwargs.pop('partial', False)
        featureTypeUid = None; projectUid= None

        if request.data.get("properties", {}):

            if  request.data.get("properties",{}).get("featureType", {}):
                featureTypeUid = request.data.get("properties").get("featureType")
            else:
                errorData.append("featureType uid not provided")
            
            # if request.data.get('properties',{}).get("project", {}):
            #     projectUid = request.data.get("properties").get("project")
            # else:
            #     errorData.append("project uid not provided")
        
        if featureTypeUid:    
            featureTypes = FeatureType.objects.filter(uid = featureTypeUid )
            if featureTypes.exists():
                request.data['properties']['featureType'] = featureTypes.first().pk
            else:
                errorData.append("featureType with uid not found")
        
        # if projectUid:
        #     projects = OrganizationProject.objects.filter(uid = projectUid)
        #     if projects.exists():
        #         project = projects.first()
        #     else:
        #         errorData.append("project with uid not found")

        if  request.data.get('properties').get('uid', ""):
            request.data.get('properties').pop('uid')

        if not errorData:
            try:
                uid = kwargs.get('uid', None)
                instance = self.get_queryset().get(uid =uid )
            except self.get_queryset().model.DoesNotExist:
                return Response({'error': True, 'errorList': 'object wit uid doesnot exist' ,'success': False, 'data': []}, status= status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)

            if serializer.is_valid():
                self.perform_update(serializer)
                returnFormat['success'] = True
                returnFormat['data'] = serializer.data
                return Response(returnFormat,status = status.HTTP_204_NO_CONTENT)
            else:
                errorData.append(serializer.errors)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

        returnFormat['error'] = True
        returnFormat['errorList'] = errorData
        return Response(returnFormat,status = status.HTTP_403_FORBIDDEN)


class FeatureRetrieveAPIView(RetrieveAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    authentication_classes = [UserAuthentication]
    permission_classes = [CanReadFeature]
    lookup_field = 'uid'

    def retrieve(self, request, *args, **kwargs):
        try:
            uid = kwargs.get('uid', None)
            instance = self.get_queryset().get(uid =uid )
        except self.get_queryset().model.DoesNotExist:
            return Response({'error': True, 'errorList': 'object wit uid doesnot exist' ,'success': False, 'data': []}, status= status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'error' : False,'data':serializer.data})


class FeatureDeleteAPIView(DestroyAPIView):

    """ Delete the Feature """

    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    authentication_classes = [UserAuthentication]
    permission_classes = [CanUpdateFeature]
    lookup_field = 'uid'

    def perform_destroy(self, instance):
       
        instance.active = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': True, 'error': False}, status=status.HTTP_204_NO_CONTENT)


    # def destroy(self, request, *args, **kwargs):
    #     import pdb;pdb.set_trace()
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
