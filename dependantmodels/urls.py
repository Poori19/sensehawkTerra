from django.conf.urls import url
from django.contrib import admin

from .views import (
    OrganizationCreateAPIView,
    OrganizationGroupCreateAPIView,
    OrganizationProjectViewSet, 
    CreateOrgGroupProjectFromJson,
    GetAllProjectsUserHasAccess
)


from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'projects', OrganizationProjectViewSet)

urlpatterns = [
    #url(r'^CreateOrgGroupProjectFromJson/$', CreateOrgGroupProjectFromJson.as_view(), name='CreateOrgGroupProjectFromJson'),
    url(r'^create/$', OrganizationCreateAPIView.as_view(), name='CreateOrg'),
    url(r'^group/create/$', OrganizationGroupCreateAPIView.as_view(), name='CreateGroup')
]

urlpatterns = urlpatterns + router.urls
