from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

def defaultPath(request):
    return render(request, "index.html")

@api_view(['GET'])
def sample_data(request):
    data = {
        'message': 'Hello from Django to Vue!'
    }
    return Response(data)