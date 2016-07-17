from django.conf.urls import url
from django.contrib import admin

from .views import *

urlpatterns = [
    url(r'^student/$', student_list, name="student_list"),
    url(r'^student/(?P<pk>\d+)$', student_detail, name="student_detail"),
    url(r'^student/query$', student_query, name="student_query"),
    url(r'^student/create$', student_create, name="student_create"),
    url(r'^student/import/$', student_import, name="student_import"),
    url(r'^record/query$', record_query, name="record_query"),
    url(r'^record/input$', record_input, name="record_input"),
    url(r'^record/analysis$', record_analysis, name="record_analysis"),
    url(r'^record/api_analysis$', api_record_analysis),
    url(r'^record/segment/$', record_segment_analysis, name="record_segment_analysis"),
    url(r'^record/average/$', record_average_analysis, name="record_average_analysis"),
    url(r'^record/average_cmp/$', record_average_cmp_analysis, name="record_average_cmp_analysis"),
    url(r'^record/level/$', record_level_analysis, name="record_level_analysis"),
]
