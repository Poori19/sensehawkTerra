# get all the fields from serializer model
from rest_framework.serializers import (
    CharField,
    EmailField,
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    ValidationError,
    SlugRelatedField,
    ListSerializer
    )

from dependantmodels.serializers import OrganizationProjectImportSerializer,OrganizationSerializer,OrganizationImportSerializer,OrganizationProjectSerializer
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Feature, FeatureType, FeatureTypeGroup
from dependantmodels.models import OrganizationProject
from drf_dynamic_fields import DynamicFieldsMixin


LIST_SERIALIZER_KWARGS = (
    'read_only', 'write_only', 'required', 'default', 'initial', 'source',
    'label', 'help_text', 'style', 'error_messages', 'allow_empty',
    'instance', 'data', 'partial', 'context', 'allow_null'
)


class FeatureTypeImportSerializer(ModelSerializer):
    class Meta:
        model = FeatureType
        fields = [
            "name",
            "uid",
            "properties"
        ]

# class FeatureTypeGroupSerializer(DynamicFieldsMixin,ModelSerializer):
#     featureTypes = SlugRelatedField(
#         many=True,
#         read_only=True,
#         slug_field='uid'
#     )

#     def to_representation(self, instance):
#         response = super().to_representation(instance)
#         if instance:
#             response['org'] = OrganizationImportSerializer(instance.org).data
#             featureTypes = instance.featureTypes.all()  
#             response['featureTypes'] = FeatureTypeImportSerializer(featureTypes, many = True).data
#             response['uid'] = instance.uid
#         return response

#     class Meta:
#         model = FeatureTypeGroup
#         fields = [
#             'name',
#             'featureTypes',
#             'org'
#         ]

class FeatureTypeGroupSerializer(DynamicFieldsMixin,ModelSerializer):
    featureTypes = FeatureTypeImportSerializer(many =True,read_only=True)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            response['uid'] = instance.uid
        return response

    class Meta:
        model = FeatureTypeGroup
        fields = [
            'name',
            'org',
            'featureTypes'
        ]



class FeatureTypeSerializer(ModelSerializer):
    class Meta:
        model = FeatureType
        fields = [
            "name",
            "org",
            "properties",
            "featureTypeGroup"
        ]
    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            response['uid'] = instance.uid
            if instance.featureTypeGroup:
                response['featureTypeGroup'] = instance.featureTypeGroup.uid
            else:
                response['featureTypeGroup'] = None
        return response


class FeatureTypeGroupSerializerCustomForList(ModelSerializer):
    class Meta:
        model = FeatureTypeGroup
        fields = [
            'name',
            'org',
        ]

class OrderedListFTSerializer(ListSerializer):
    
    @property
    def data(self):
        return super(ListSerializer, self).data

    def to_representation(self, data):
        """
        returns the model instance in this json format
        """

        orderFTbyFTG = []
        FTGids = list(data.values_list('featureTypeGroup', flat = True).distinct())
        ftgs = FeatureTypeGroup.objects.filter(id__in = FTGids)
        
        for ftg in ftgs:
            ftgSerializer = FeatureTypeGroupSerializerCustomForList(ftg)
            ftgSerializerData = ftgSerializer.data
            #groupSerializerData['projects'] = []
            fts = data.filter(featureTypeGroup = ftg)
            ftgSerializerData['featureTypes'] = []
            for ft in fts:
                ftgSerializerData['featureTypes'].append(dict(self.child.to_representation(ft)))
            orderFTbyFTG.append(ftgSerializerData)
        return orderFTbyFTG

class OrderedListFTByFTG(ModelSerializer):
    
    @classmethod
    def many_init(cls, *args, **kwargs):
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {'child': child_serializer}
        list_kwargs.update(dict([
            (key, value) for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        ]))
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', OrderedListFTSerializer)
        return list_serializer_class(*args, **list_kwargs)

    class Meta:
        model = FeatureType
        fields = [
            "name",
            "org",
            "properties",
            "uid"
        ]


class FeatureTypeCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = FeatureType
        fields = [
            "name",
            "org",
            "properties"
        ]
    
    



class FeatureTypeGroupCustomSerializer(DynamicFieldsMixin,ModelSerializer):

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance:
            response['uid'] = instance.uid
            featureTypes = FeatureType.objects.filter(featureTypeGroup = instance)
            response['featureTypes'] = FeatureTypeCreateUpdateSerializer(featureTypes, many=True).data
        return response

    class Meta:
        model = FeatureTypeGroup
        fields = [
            'name',
            'org'
        ]



class FeatureCreateUpdateSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Feature
        geo_field = "geometry"
        fields = [   
            "name",
            "description",
            "featureType",
            "project",
            "geometry",
            "hierarchyProperties", 
            "dataProperties",
            "extraProperties"
        ]

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.featureType:
            response['properties']['featureType'] = instance.featureType.uid
        if instance.uid:
            response['properties']['uid'] = instance.uid
        return response

  

    def validate_project(self, value):
        # validation process...
        if not value:
            raise ValidationError("project uid is required")
        return value

    

    
class FeatureSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    project = OrganizationProjectImportSerializer(read_only = True)
    featureType = FeatureTypeSerializer(read_only = True)

    class Meta:
        model = Feature
        geo_field = "geometry"

        fields = [   
                    "uid",
                    "name",
                    "description",
                    "featureType",
                    "project",
                    "geometry",
                    "dataProperties",
                    "hierarchyProperties",
                    "extraProperties"

                ]


  

