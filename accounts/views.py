from django.shortcuts import render
import json
from django.http import HttpResponse
from django.http import JsonResponse
import environ
env = environ.Env()

# Create your views here.

def detail(request):
    tokendata = {}
    if request.user:
        tokendata['user'] = str(request.user)

    return JsonResponse(tokendata)

