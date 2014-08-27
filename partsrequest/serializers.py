
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.compat import BytesIO
from models import PartsRequest, RequestDetail
from dept.models import Employee


class RequestDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestDetail
        fields = ('pn', 'bin', 'description', 'qty', 'actual_qty', 'unit',
                  'over_plan_usage', 'balance', 'usage_by_once', 'remark')
        

class PartsRequestSerializer(serializers.ModelSerializer):
    requestdetail_set = RequestDetailSerializer(many=True)
    employee = serializers.SlugRelatedField(slug_field='num')

    def restore_object(self, attrs, instance=None):
        inst = super(PartsRequestSerializer, self).restore_object(attrs, instance)
        if "approver" in attrs:
            approver_nums = JSONParser().parse(BytesIO(attrs.get('approver')))
            approver_ids = map(lambda num: str(Employee.objects.get(num=num).id), approver_nums)
            inst.approver = ",".join(approver_ids)
        return inst

    def transform_approver(self, obj, value):
        uids = value.split(',')
        nums = map(lambda uid: Employee.objects.get(id = int(uid) ).num, uids)
        return JSONRenderer().render(nums)
    
    class Meta:
        model = PartsRequest
        fields = ('request_no', 'apply_type', 'material_type', 'apply_reason', 'employee',
                  'cost_center', 'approver', 'request_date', 'requestdetail_set')


