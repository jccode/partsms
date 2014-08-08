from django.conf.urls import patterns, include, url
from partsrecycle import views

urlpatterns = patterns(
    '', 
    url(r'^permissiondenied/$', views.permission_denied_view, name='permission_denined_view'),
)

handler403 = 'partsrecycle.views.permission_denied_view'

