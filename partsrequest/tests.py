
from django.test import TestCase
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.compat import BytesIO
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient
from datetime import datetime
import operator, urllib2, base64
from dept.models import Employee
from models import PartsRequest, RequestDetail
from serializers import PartsRequestSerializer
import pdb

# Create your tests here.

json_data = '{"request_no": "A201404001024", "apply_type": "app_type", "material_type": "mtype", "apply_reason": "aReason", "employee": "9527", "cost_center": "34E110", "approver": "[\\"9527\\", \\"9528\\"]", "request_date": "2014-08-27T12:30:00.000Z", "requestdetail_set": [{"pn": "110290", "bin": "L5A201", "description": "Gasket Retainer Ass", "qty": 10, "actual_qty": null, "unit": "pcs", "over_plan_usage": null, "balance": "100", "usage_by_once": null, "remark": ""}, {"pn": "110291", "bin": "E5B401", "description": "Gasket Retainer Ass", "qty": 5, "actual_qty": null, "unit": "pcs", "over_plan_usage": null, "balance": "50", "usage_by_once": null, "remark": ""}]}'

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
        json = json_data
        data = JSONParser().parse(BytesIO(json))
        ser = PartsRequestSerializer(data=data)
        self.assertTrue(ser.is_valid())
        ser.save()
        preq = ser.object
        self.assertEqual(preq.request_no, "A201404001024") # request_no
        self.assertEqual(preq.approver, u"101,102")        # approver
        self.assertEqual(preq.requestdetail_set.count(), 2) # request detail

    def test_parts_request_deserialize_with_not_exist_num(self):
        json = json_data.replace('9528', '9999')
        data = JSONParser().parse(BytesIO(json))
        ser = PartsRequestSerializer(data=data)
        self.assertTrue(ser.is_valid())
        e = Employee.objects.get(num='9999')
        self.assertNotEqual(e, None)
        
        
class PartsRequestAPITest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.username1 = 'u_with_p'
        cls.password1 = 'pass'
        cls.user1 = User.objects.create_user(username=cls.username1, password=cls.password1)
        content_type_ids = map(lambda m: ContentType.objects.get_for_model(m).pk, [PartsRequest, RequestDetail])
        permissions = [ Permission.objects.filter(content_type_id=id) for id in content_type_ids ]
        permissions = [ p for perms in permissions for p in perms ] # flatten
        for p in permissions:
            cls.user1.user_permissions.add(p)
        cls.user1 = User.objects.get(pk = cls.user1.pk)
        
        cls.username2 = 'u_without_p'
        cls.password2 = 'pass'
        cls.user2 = User.objects.create_user(username=cls.username2, password=cls.password2)

        cls.factory = APIRequestFactory()
        cls.url = '/api/partsrequest/'
        # cls.client = APIClient()
        Employee.objects.create(user=cls.user1, num='9527', pk=101)
        Employee.objects.create(user=cls.user2, num='9528', pk=102)
        
    @classmethod
    def tearDownClass(cls):
        cls.user1.delete()
        cls.user2.delete()

    def login_with_user1(self):
        return self.client.login(username=self.username1, password=self.password1)

    def login_with_user2(self):
        return self.client.login(username=self.username2, password=self.password2)
    
    def test_initdata_created(self):
        self.assertTrue( self.login_with_user1() )
        self.assertTrue( self.login_with_user2() )
        info_pr = (PartsRequest._meta.app_label, PartsRequest._meta.model_name)
        info_rd = (RequestDetail._meta.app_label, RequestDetail._meta.model_name)
        self.assertTrue( self.user1.has_perm('%s.add_%s' % info_pr) )
        self.assertTrue( self.user1.has_perm('%s.change_%s' % info_rd) )
        self.assertFalse( self.user2.has_perm('%s.add_%s' % info_pr) )
        self.assertFalse( self.user2.has_perm('%s.change_%s' % info_rd) )

    def test_user_need_to_login_to_call_api(self):
        resp = self.client.get(self.url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, resp.status_code)
        self.login_with_user1()
        resp = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, resp.status_code)

    def test_get_list_data(self):
        self.assertTrue(True)
        self.login_with_user1()
        resp = self.client.get(self.url)
        self.assertEqual(status.HTTP_200_OK, resp.status_code)

    def test_post_data_forbidden_as_not_login(self):
        resp = self.client.post(self.url, content_type='application/json', data=json_data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, resp.status_code)
        
    def test_post_data_forbidden_as_have_not_permission(self):
        self.login_with_user2()
        resp = self.client.post(self.url, content_type='application/json', data=json_data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, resp.status_code)
        self.client.logout()
        
    def test_post_data(self):
        c1 = PartsRequest.objects.count()
        self.login_with_user1()
        resp = self.client.post(self.url, content_type='application/json', data=json_data)
        self.assertTrue(status.is_success(resp.status_code))
        self.assertEqual(c1+1, PartsRequest.objects.count())
    

        
    
