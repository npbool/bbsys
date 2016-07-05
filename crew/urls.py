from django.conf.urls import url
from django.contrib import admin

from .views import *


urlpatterns = [
    url(r'^$', query, name="query"),
    url(r'^student/$', student_list, name="student_list"),
]
