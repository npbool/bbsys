from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Semester)
admin.site.register(Exam)
admin.site.register(Record)
admin.site.register(Department)
admin.site.register(Person)