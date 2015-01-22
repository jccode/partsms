from django.conf.urls import patterns, include, url
from views import EmployeeList

urlpatterns = patterns(
    '', 
    url(r'^api/employee/', EmployeeList.as_view()),
)

