
from rest_framework import serializers
from models import PartsRequest, RequestDetail
from dept.serializers import EmployeeRefSerializer


class RequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestDetail
        fields = ('pn', 'bin', 'description', 'qty', 'actual_qty', 'unit',
                  'over_plan_usage', 'balance', 'usage_by_once', 'remark')
        

class PartsRequestSerializer(serializers.ModelSerializer):
    details = RequestDetailSerializer(many=True)
    
    class Meta:
        model = PartsRequest
        fields = ('request_no', 'apply_type', 'material_type', 'apply_reason', 'employee',
                  'cost_center', 'approver', 'request_date', 'details')
        

