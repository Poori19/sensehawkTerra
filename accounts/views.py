# from django.shortcuts import render
# import json
# from django.http import HttpResponse
# from django.http import JsonResponse
# import environ
# env = environ.Env()

#from broker.settings.message_broker import conn

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.authentication import UserAuthentication

class userDetail(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all users.
        """ 
        user = {}
        if self.request.user:
            user  = str(self.request.user)
        return Response(user)

