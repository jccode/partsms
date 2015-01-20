# -*- coding: utf-8 -*-

from selectable.base import ModelLookup
from selectable.registry import registry
from dept.models import Employee
from selectable.decorators import login_required

@login_required
class EmployeeLookup(ModelLookup):
    model = Employee
    search_fields = ('num__icontains', 'user__username__icontains', 'user__first_name__icontains', 'user__last_name__icontains')
    # search_fields = ('user__username', )

    def employee_str(self, item):
        """
        This function should return a string
        """
        if type(item) is Employee:
            if item.user.last_name and item.user.first_name:
                val = item.user.last_name + item.user.first_name
            elif item.user.first_name and not item.user.last_name:
                val = item.user.first_name
            else:
                val = item.user.username
            return val
        else:
            return item

    def get_item_id(self, item):
        """
        The id is the value that will eventually be returned by the field/widget. 
        Should return a string.
        """
        return self.employee_str(item)
            
    def get_item_value(self, item):
        return self.employee_str(item)

    def get_item_label(self, item):
        return self.employee_str(item)
    
    def get_item(self, value):
        return value
        

    
registry.register(EmployeeLookup)

