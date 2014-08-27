from django.shortcuts import render
from rest_framework import viewsets
from models import PartsRequest
from serializers import PartsRequestSerializer


# Create your views here.

class PartsRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for parts request
    """
    queryset = PartsRequest.objects.all()
    serializer_class = PartsRequestSerializer

