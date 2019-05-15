from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField 
from django.db.models.signals import pre_save,post_save
from accounts.constants import Constants
from accounts.utils import RandomStringGenerator

class Element(models.Model):
    
    uid = models.CharField(max_length=220,unique = True,editable = False)
    
    # Below the mandatory fields for generic relation
    #content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    #object_id = models.PositiveIntegerField()
    #content_object =  GenericForeignKey('content_type', 'object_id')

def create_uid(instance, new_uid=None):

    uid = RandomStringGenerator().randomstring(12)   
    if new_uid is not None:
        uid = new_uid
    qs = instance._meta.model.objects.filter(uid=uid)

    # if exists
    if  qs.exists():
        uid = RandomStringGenerator().randomstring1(Constants.UID_LENGTH)   
        return create_uid(instance, new_uid=uid)
    return uid

def pre_save_uid_receiver(sender, instance, *args, **kwargs):
    if not instance.uid:
        uid = RandomStringGenerator().randomstring(Constants.UID_LENGTH)   
        instance.uid = create_uid(instance,uid)

pre_save.connect(pre_save_uid_receiver, sender=Element)