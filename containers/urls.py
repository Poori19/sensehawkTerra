
from django.conf.urls import url
from django.contrib import admin

from .views import (
    ContainerViewCreateAPIView,
    CreateOrUpdateOrgContainerAndAttachGroupsFromJson,
    ContainerViewListAPIView,
    ContainerViewRetrieveAPIView,
    AddFTGToContainerView,
    RemoveFTGToContainerView
)

urlpatterns = [
    url(r'^create/$', ContainerViewCreateAPIView.as_view(), name='create'),
    url(r'^$', ContainerViewListAPIView.as_view(), name='list'),
    url(r'^(?P<uid>[^/.]+)/$', ContainerViewRetrieveAPIView.as_view(), name='retrieve'),
    #url(r'^CreateUpdateOrgContainerAndAttachGroupsFromJson/$', CreateOrUpdateOrgContainerAndAttachGroupsFromJson.as_view(), name='CreateOrUpdateOrgContainerAndAttachGroupsFromJson'),
    url(r'^(?P<uid>[^/.]+)/ftg/add/$', AddFTGToContainerView.as_view(), name='add_feature_type_group_to_container_view'),
    url(r'^(?P<uid>[^/.]+)/ftg/remove/$', RemoveFTGToContainerView.as_view(), name='remove_feature_type_group_to_container_view'),
]