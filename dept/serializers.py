
from rest_framework import serializers
from models import Employee


class EmployeeRefSerializer(serializers.Serializer):
    num = serializers.CharField(max_length=20)

    def restore_object(self, attrs, instance=None):
        """
        Restore objects.
        
        Arguments:
        - `self`:
        - `attrs`:
        - `instance`:
        """
        if 'num' in attrs:
            n = attrs.get('num')
            employees = Employee.objects.filter(num = n)
            if len(employees) > 0:
                return employees[0]
        else:
            return None    
        
        
