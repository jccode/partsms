# -*- coding: utf-8 -*-

from selectable.base import ModelLookup
from selectable.registry import registry
# from django.contrib.auth.models import User
from selectable.decorators import login_required
from dept.models import Employee
from utils import user_str

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
            return user_str(item.user)
        else:
            return item

    def get_item_id(self, item):
        """
        The id is the value that will eventually be returned by the field/widget. 
        Should return a string.
        """
        # return self.employee_str(item)
        if type(item) is Employee:
            return item.user.username
        else:
            return item
            
    def get_item_value(self, item):
        """
        This is last of three formatting methods. The value is shown in the input once
        the item has been selected.
        """
        # return self.employee_str(item)
        if type(item) is Employee:
            return item.user.username
        else:
            return item

    def get_item_label(self, item):
        """
        This is first of three formatting methods. The label is shown in the drop down
        menu of search results.
        """
        return self.employee_str(item)
    
    def get_item(self, value):
        """
        get_item is the reverse of get_item_id. This should take the value from the form
        initial values and return the current item. This defaults to simply return the
        value.
        """
        try:
            u = Employee.objects.get(user__username=value)
            return self.employee_str(u)
        except Exception as e:
            return value

    def create_item(self, value):
        """
        If you plan to use a lookup with a field or widget which allows the user to
        input new values then you must define what it means to create a new item for
        your lookup. By default this raises a NotImplemented error.
        """
        return value
        
    
registry.register(EmployeeLookup)

