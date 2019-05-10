from django.conf.urls import url

from .views import userDetail,ListObjectPermissions

urlpatterns = [
    url(r'^user-detail/$',userDetail.as_view(), name='userDetail'),
    url(r'^list-object-permissions/$',ListObjectPermissions.as_view(), name='List Object Permissions'),
]
