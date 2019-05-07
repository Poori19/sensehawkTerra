from django.conf.urls import url

from .views import userDetail

urlpatterns = [
    url(r'^detail/$',userDetail.as_view(), name='userDetail'),
]
