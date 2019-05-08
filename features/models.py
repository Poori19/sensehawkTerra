from django.contrib.gis.db import models


from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from dependantmodels.models import Organization,OrganizationProject
from accounts.utils import RandomStringGenerator


class FeatureTypeGroup(models.Model):

    uid = models.CharField(max_length=220,unique = True,editable = False)
    name  = models.CharField(max_length=220)
    active =  models.BooleanField(default=True)
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True) 
    owner = JSONField()

    def __str__(self):
        return self.name

class FeatureType(models.Model):
    name  = models.CharField(max_length=220)
    uid = models.CharField(max_length=220,unique = True,editable = False)
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True) 
    featureTypeGroup = models.ForeignKey(FeatureTypeGroup,related_name='featureTypes', on_delete=models.SET_NULL, null=True, blank = True)
    active =  models.BooleanField(default=True)
    owner = JSONField()
    properties = JSONField(null = True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        #ordering = ["-name"]
        indexes = [
            models.Index(fields=['uid','org'], name='uid_org_idx'),
        ]

class Feature(models.Model):
    """
        Creating the model FEATURE
        The foreign key projects has to be in the given views
    """
    uid = models.CharField(max_length=220,unique = True,editable = False)
    name  = models.CharField(max_length=220, blank=True, null=True)
    description =  models.TextField(null = True)
    featureType = models.ForeignKey(FeatureType, on_delete=models.SET_NULL, null=True, blank = True)
    project = models.ForeignKey(OrganizationProject, on_delete=models.SET_NULL, null=True,blank = True)
    geometry = models.PolygonField()
    dataProperties = JSONField(null = True)
    hierarchyProperties = JSONField(null = True)
    extraProperties = JSONField(null = True)
    owner = JSONField(null = True)
    active =  models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.uid

    class Meta:
        #ordering = ["-name"]
        indexes = [
            models.Index(fields=['uid'], name='uid_idx'),
        ]


def create_uid(instance, new_uid=None):

    uid = RandomStringGenerator().randomstring(12)   
    if new_uid is not None:
        uid = new_uid
    qs = instance._meta.model.objects.filter(uid=uid)

    # if exists
    if  qs.exists():
        uid = RandomStringGenerator().randomstring(12)   
        return create_uid(instance, new_uid=uid)
    return uid

def pre_save_uid_receiver(sender, instance, *args, **kwargs):
    if not instance.uid:
        uid = RandomStringGenerator().randomstring(12)   
        instance.uid = create_uid(instance,uid)

pre_save.connect(pre_save_uid_receiver, sender=FeatureType)
pre_save.connect(pre_save_uid_receiver, sender=Feature)
pre_save.connect(pre_save_uid_receiver, sender=FeatureTypeGroup)
