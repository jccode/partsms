from django.conf.urls import patterns, include, url
from partsapp import views

urlpatterns = patterns(
    '', 
    url(r'^permissiondenied/$', views.permission_denied_view, name='permission_denined_view'),
)

handler403 = 'partsapp.views.permission_denied_view'

