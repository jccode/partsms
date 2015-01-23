
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
# from rest_framework.compat import BytesIO
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from dept.models import Employee
from models import PartsRequest, RequestDetail
from dept.models import Employee


class RequestDetailSerializer(serializers.ModelSerializer):        
    class Meta:
        model = RequestDetail
        fields = ('pn', 'bin', 'description', 'qty', 'actual_qty', 'unit',
                  'over_plan_usage', 'balance', 'usage_by_once', 'remark')

        
class PartsRequestSerializer(serializers.ModelSerializer):
    requestdetail_set = RequestDetailSerializer(many=True)

    def create(self, validated_data):
        requestdetail_set = validated_data.pop('requestdetail_set')
        pq = PartsRequest(**validated_data)
        pds = map(lambda data: RequestDetail(**data), requestdetail_set)
        pq.requestdetail_set = pds
        pq.save()
        return pq
    
    class Meta:
        model = PartsRequest
        fields = ('request_no', 'apply_type', 'material_type', 'apply_reason', 'employee',
                  'employee_num', 'department', 'cost_center', 'approver', 'request_date',
                  'requestdetail_set')
    


