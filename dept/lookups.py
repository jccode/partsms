# -*- coding: utf-8 -*-

from selectable.base import ModelLookup
from selectable.registry import registry
from dept.models import Employee

class EmployeeLookup(ModelLookup):
    model = Employee
    search_fields = ('num__icontains', 'user__username__icontains', 'user__first_name__icontains', 'user__last_name__icontains')
    # search_fields = ('user__username', )

    
registry.register(EmployeeLookup)

