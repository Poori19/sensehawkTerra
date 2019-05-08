# get all the fields from serializer model
import collections
from collections import OrderedDict


LIST_SERIALIZER_KWARGS = (
    'read_only', 'write_only', 'required', 'default', 'initial', 'source',
    'label', 'help_text', 'style', 'error_messages', 'allow_empty',
    'instance', 'data', 'partial', 'context', 'allow_null'
)

from drf_dynamic_fields import DynamicFieldsMixin


from django.urls import reverse
from rest_framework.serializers import (
    IntegerField,
    CharField,
    ListField,
    EmailField,
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
    ListSerializer,
    PrimaryKeyRelatedField
    )

from .models import (
    OrganizationProject, 
    Organization, 
    OrganizationGroup,
    ContainerView
)

from .data import OrganizationProjectData

class OrganizationImportSerializer(DynamicFieldsMixin,ModelSerializer):
    class Meta:
        model = Organization
        fields = [ "uid",
                    "name",
                ]

    
class OrganizationGroupImportSerializer(ModelSerializer):
    class Meta:
        model = OrganizationGroup
        fields = [ "uid",
                    "name",
        ]

class OrganizationProjectImportSerializer(ModelSerializer):
    class Meta:
        model = OrganizationProject
        fields = [ "uid",
                    "name",
        ]

            
class OrganizationSerializer(DynamicFieldsMixin,ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class OrganizationGroupSerializer(DynamicFieldsMixin,ModelSerializer):
    class Meta:
        model = OrganizationGroup
        fields = '__all__'


class OrganizationGroupCreateUpdateSerializer(ModelSerializer):
    class Meta: 
        model = OrganizationGroup
        fields = [
            'organization',
            'name',  
            'uid',
            'containerView',
            'description',
            'readUsers', 
            'writeUsers', 
            'readLabels',
            'writeLabels'
        ]

class OrganizationCreateUpdateSerializer(ModelSerializer):
    class Meta: 
        model = Organization
        fields = [
            'uid',
            'name', 
            'active',
            'description',
            'readUsers', 
            'writeUsers', 
            'readLabels',
            'writeLabels'
        ]


class OrganizationProjectSerializer(DynamicFieldsMixin,ModelSerializer):
    class Meta:
        model = OrganizationProject
        fields = [
            'uid',
            'name',
            'active',
            'readUsers', 
            'writeUsers', 
            'description',
            'readLabels',
            'writeLabels',
            'data',
            'group'
        ]


class OrganizationProjectSerializerWithData(DynamicFieldsMixin,ModelSerializer):

    vectors = SerializerMethodField('get_vectors_details')
    def to_representation(self, instance):
        data = None
        response = super().to_representation(instance)
        if instance and instance.data:
            reportData = OrganizationProjectData.send_urls_and_pre_signed_urls_data(instance.data)
            response['reports'] = reportData
        return response
    class Meta:
        model = OrganizationProject
        fields = [
            'uid',
            'name',
            'active',
            'readUsers', 
            'writeUsers', 
            'description',
            'readLabels',
            'writeLabels',
            'group',
            'vectors'
        ]

    def get_vectors_details(self, obj):
        return ("/features/project/" + obj.uid)
        

class OrganizationGroupSerializerProjectsPerGroup(ModelSerializer):
    
    def to_representation(self, instance): 
        response = super().to_representation(instance)
        if instance:
            projects = instance.organizationproject_set.all()
            response['projects'] = OrganizationProjectSerializerWithData(projects, many = True).data   
        return response
    class Meta:
        model = OrganizationGroup
        fields = [ "uid",
                    "name"
        ]


class OrderedListProjectSerializer(ListSerializer):
    
    @property
    def data(self):
        return super(ListSerializer, self).data

    def to_representation(self, data):
        """
        returns the model instance in this json format
        """
        orderProjectsPerGroup = []
        groupsUids = list(data.values_list('group', flat = True).distinct())
        groups = OrganizationGroup.objects.filter(uid__in = groupsUids)
        
        for group in groups:
            groupSerializer = OrganizationGroupImportSerializer(group)
            groupSerializerData = groupSerializer.data
            #groupSerializerData['projects'] = []
            projects = data.filter(group = group)
            groupSerializerData['projects'] = []
            for project in projects:
                groupSerializerData['projects'].append(dict(self.child.to_representation(project)))
            orderProjectsPerGroup.append(groupSerializerData)
        return orderProjectsPerGroup

    


class OrderedListProjectGroupByGroupSerializer(ModelSerializer):
    
    @classmethod
    def many_init(cls, *args, **kwargs):
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {'child': child_serializer}
        list_kwargs.update(dict([
            (key, value) for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        ]))
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', OrderedListProjectSerializer)
        return list_serializer_class(*args, **list_kwargs)

    class Meta:
        model = OrganizationProject
        fields = [
            'uid',
            'name'
        ]

