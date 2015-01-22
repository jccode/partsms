
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
    
    class Meta:
        model = PartsRequest
        fields = ('request_no', 'apply_type', 'material_type', 'apply_reason', 'employee',
                  'employee_num', 'department', 'cost_center', 'approver', 'request_date',
                  'requestdetail_set')
    

to_be_removed = """        
class PartsRequestSerializer(serializers.ModelSerializer):
    requestdetail_set = RequestDetailSerializer(many=True)
    employee = serializers.SlugRelatedField(slug_field='num')

    def get_employee_id_by_num(self, num):
        try:
            e = Employee.objects.get(num=num)
        except ObjectDoesNotExist as e:
            u = User.objects.create_user(username=num, password=num)
            e = Employee.objects.create(user=u, num=num)
        return e.id
    
    def restore_object(self, attrs, instance=None):
        inst = super(PartsRequestSerializer, self).restore_object(attrs, instance)
        if "approver" in attrs:
            approver_nums = JSONParser().parse(BytesIO(attrs.get('approver')))
            # TODO: if the emplee num doesn't founded, it will create a new employee
            approver_ids = map(lambda num: str(self.get_employee_id_by_num(num)), approver_nums)
            inst.approver = ",".join(approver_ids)
        return inst

    def transform_approver(self, obj, value):
        if not value:
            return ""
        uids = value.split(',')
        nums = map(lambda uid: Employee.objects.get(id = int(uid) ).num, uids)
        return JSONRenderer().render(nums)
    
    class Meta:
        model = PartsRequest
        fields = ('request_no', 'apply_type', 'material_type', 'apply_reason', 'employee',
                  'cost_center', 'approver', 'request_date', 'requestdetail_set')
"""



