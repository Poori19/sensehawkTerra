from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinLengthValidator
#from features.models import FeatureTypeGroup


# Create your models here.

class Organization(models.Model):

    uid =  models.CharField(max_length=120, primary_key = True, validators=[MinLengthValidator(1)])
    name  = models.CharField(max_length=220, blank=True, null=True,unique = True)
    description =  models.TextField(null = True, blank = True)
    active =  models.BooleanField(default=True)
    owner = JSONField(null = True)
    readUsers = JSONField(null = True)
    writeUsers = JSONField(null = True)
    readLabels = JSONField(null = True)
    writeLabels = JSONField(null = True)

    def __str__(self):
        return self.name


class ContainerView(models.Model):

    uid = models.CharField(max_length=220,primary_key = True, validators=[MinLengthValidator(1)])
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    featureTypeGroups = models.ManyToManyField('features.FeatureTypeGroup')
    name  = models.CharField(max_length=220, blank=True, null=True)
    description =  models.TextField(null = True, blank = True)
    active =  models.BooleanField(default=True)
    owner = JSONField(null = True)

    readUsers = JSONField(null = True)
    writeUsers = JSONField(null = True)
    readLabels = JSONField(null = True)
    writeLabels = JSONField(null = True)

    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return self.name


class OrganizationGroup(models.Model):
    
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    containerView = models.ForeignKey(ContainerView, on_delete=models.SET_NULL, null=True)
    uid =  models.CharField(max_length=220,primary_key = True,validators=[MinLengthValidator(1)])
    name  = models.CharField(max_length=220, blank=True, null=True)
    description =  models.TextField(null = True, blank = True)
    active =  models.BooleanField(default=True)
    owner = JSONField(null = True)
    readUsers = JSONField(null = True)
    writeUsers = JSONField(null = True)
    readLabels = JSONField(null = True)
    writeLabels = JSONField(null = True)

    def __str__(self):
        return self.name

        
class OrganizationProject(models.Model):

    group = models.ForeignKey(OrganizationGroup, on_delete=models.SET_NULL, null=True)
    uid =  models.CharField(max_length=220,primary_key = True,validators=[MinLengthValidator(1)])
    name  = models.CharField(max_length=220, blank=True, null=True)
    description =  models.TextField(null = True, blank = True)
    active =  models.BooleanField(default=True)
    owner = JSONField(null = True)
    data = JSONField(null = True)
    readUsers = JSONField(null = True)
    writeUsers = JSONField(null = True)
    readLabels = JSONField(null = True)
    writeLabels = JSONField(null = True)

    def __str__(self):
        return self.name

    @staticmethod
    def TestStaticMethod(name):
        return "worked"
        

