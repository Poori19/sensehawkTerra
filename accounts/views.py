# from django.shortcuts import render
# import json
# from django.http import HttpResponse
# from django.http import JsonResponse
# import environ
# env = environ.Env()

from broker.settings.message_broker import conn
from django.contrib.contenttypes.models import ContentType        

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import UserAuthentication
from general.permissions import SuperUserPermission

class userDetail(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all users.
        """ 
        user = {}
        if self.request.user:
            user  = self.request.user
        return Response(user)

class ListObjectPermissions(APIView):
    #authentication_classes = (UserAuthentication,)
    authentication_classes = [UserAuthentication]
    permission_classes = [SuperUserPermission]

    def get(self, request, *args, **kwargs):
        """
        return the permissions of the obj
        """ 

        data = {}
        data['user'] = self.request.user

        if request.GET.get('model') and request.GET.get('uid'):
            model = request.GET.get('model')
            uid = request.GET.get('uid')
            contentTypes =ContentType.objects.filter( model=model)  
            if contentTypes.exists():
                contentType = contentTypes.first()
                data['obj'] = contentType.get_all_objects_for_this_type().filter(uid= uid).values('writeUsers', 'writeLabels', 'readUsers', 'readLabels')
        
        return Response(data)

