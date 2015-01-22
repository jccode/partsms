from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import generics
from models import Employee
from serializers import EmployeeSerializer

# Create your views here.

class EmployeeList(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_fields = ('num', 'user__username')
        

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    
