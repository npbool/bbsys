from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from .models import *

# Register your models here.
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Semester)
admin.site.register(Grade)
admin.site.register(Exam)
admin.site.register(Record)
admin.site.register(Department)
admin.site.register(Person)
admin.site.register(SystemSettings)
# admin.site.register(Staff)
admin.site.register(ClassTeacher)
admin.site.register(Leader)
admin.site.register(SubjectLeader)


class StaffInline(admin.StackedInline):
    model = Staff
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    inlines = [StaffInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
