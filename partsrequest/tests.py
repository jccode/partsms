
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.compat import BytesIO
from datetime import datetime
from dept.models import Employee
from models import PartsRequest, RequestDetail
from serializers import PartsRequestSerializer

# Create your tests here.

class PartsRequestSerializerTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user1 = User.objects.create(username='bohu.tang')
        cls.user2 = User.objects.create(username='zhishang.zhu')
        cls.employee1 = Employee.objects.create(user=cls.user1, num='9527', pk=101)
        cls.employee2 = Employee.objects.create(user=cls.user2, num='9528', pk=102)

    @classmethod
    def tearDownClass(cls):
        cls.user1.delete()
        cls.employee1.delete()
        
    def setUp(self):
        """
        """
        pass

    def test_simple_add(self):
        self.assertEqual(1+1, 2)

    def test_initdata_created(self):
        u = User.objects.get(username='bohu.tang')
        self.assertEqual(u, self.user1)
        e = Employee.objects.get(num='9527')
        self.assertEqual(e, self.employee1)
        
        es = Employee.objects.all()
        self.assertEqual(len(es), 2)
        nums = map(lambda e: e.num, es)
        self.assertEqual(nums, [u'9527', u'9528'])
        
    def test_parts_request_serialize(self):
        preq = PartsRequest(request_no='A201404001024',apply_type='app_type',material_type='mtype',
                            apply_reason='aReason',employee=self.employee1,cost_center='34E110',
                            request_date=datetime.now(),approver="101,102")
        reqdetail = RequestDetail(request=preq, pn='120291',bin='M5N101',description='Parts name',qty=10,
                                  actual_qty=5, unit='pcs',balance=100)
        preq.save()
        reqdetail.save()
        pqser = PartsRequestSerializer(preq)
        json = JSONRenderer().render(pqser.data)
        self.assertTrue( 'A201404001024' in json ) # request_no
        self.assertTrue( '9527' in json and '9528' in json ) # approver
        self.assertTrue( '120291' in json )                  # requeset detail pn
        
    def test_parts_request_deserialize(self):
        json = '{"request_no": "A201404001024", "apply_type": "app_type", "material_type": "mtype", "apply_reason": "aReason", "employee": "9527", "cost_center": "34E110", "approver": "[\\"9527\\", \\"9528\\"]", "request_date": "2014-08-27T12:30:00.000Z", "requestdetail_set": [{"pn": "110290", "bin": "L5A201", "description": "Gasket Retainer Ass", "qty": 10, "actual_qty": null, "unit": "pcs", "over_plan_usage": null, "balance": "100", "usage_by_once": null, "remark": ""}, {"pn": "110291", "bin": "E5B401", "description": "Gasket Retainer Ass", "qty": 5, "actual_qty": null, "unit": "pcs", "over_plan_usage": null, "balance": "50", "usage_by_once": null, "remark": ""}]}'
        data = JSONParser().parse(BytesIO(json))
        ser = PartsRequestSerializer(data=data)
        self.assertTrue(ser.is_valid())
        ser.save()
        preq = ser.object
        self.assertEqual(preq.request_no, "A201404001024") # request_no
        self.assertEqual(preq.approver, u"101,102")        # approver
        self.assertEqual(preq.requestdetail_set.count(), 2) # request detail
        
        
