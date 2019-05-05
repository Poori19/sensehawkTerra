import collections
from collections import OrderedDict
from rest_framework.serializers import (
    CharField,
    EmailField,
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
    ListSerializer
    )


LIST_SERIALIZER_KWARGS = (
    'read_only', 'write_only', 'required', 'default', 'initial', 'source',
    'label', 'help_text', 'style', 'error_messages', 'allow_empty',
    'instance', 'data', 'partial', 'context', 'allow_null'
)
from .models import Element
from drf_dynamic_fields import DynamicFieldsMixin


class ElementSerializer(ModelSerializer):
    class Meta:
        model = Element
        fields = [
            "content_type",
            "object_id"
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance and instance.uid:
            response['uid'] = instance.uid
        if instance
        return response



