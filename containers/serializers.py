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

from dependantmodels.models import ContainerView
class ContainerViewSerializer(ModelSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            response['active'] = instance.active
            response['featureTypeGroups'] = instance.featureTypeGroups.all().values_list('uid', flat = True)
        return response

    class Meta:
        model = ContainerView
        fields = [
            'uid',
            'name',
            'description',
            'owner',
            'readUsers',
            'writeUsers',
            'readLabels',
            'writeLabels',
            'organization'   
        ]