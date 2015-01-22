# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from rest_framework import routers, serializers, viewsets

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'partsms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
    url(r'', include(admin.site.urls)),
    
    # django admin_tools
    url(r'^admin_tools/', include('admin_tools.urls')),
    
    url(r'^parts/', include('partsrecycle.urls')),

    # django-selectable
    (r'^selectable/', include('selectable.urls')),

    # Apps urls
    url(r'', include('dept.urls')), 
)


# restful url
from partsrequest.views import PartsRequestViewSet
from dept.views import EmployeeViewSet

router = routers.DefaultRouter()
router.register(r'partsrequest', PartsRequestViewSet)
router.register(r'employee', EmployeeViewSet)

urlpatterns += patterns(
    '',
    url(r'^api/', include(router.urls)), 
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')), 
)


