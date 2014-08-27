
from django.conf.urls import patterns, url, include
from rest_framework import routers
import views

router = routers.DefaultRouter()
router.register(r'partsrequest', views.PartsRequestViewSet)

# Wire up our API using automatic URL routing
urlpatterns = patterns(
    '',
    url(r'^api/', include(router.urls)), 
)


