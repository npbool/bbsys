# coding: utf8
from django.db import models
from .util import *


# Create your models here.
class Student(models.Model):
    student_id = models.CharField(max_length=7)
    national_id = models.CharField(max_length=18)
    name = models.CharField(max_length=6)
    gender = models.CharField(max_length=1, choices=Choices.GENDER_CHOICES)
    birth_date = models.DateField()

    ethnicity = models.CharField(max_length=10)
    native_place = models.CharField(max_length=30)
    political_status = models.CharField(max_length=2, choices=Choices.POLITICAL_CHOICES)

    hukou_is_agri = models.BooleanField(choices=Choices.HUKOU_CHOICES)

    SCHOOL_BB = "BB"
    SCHOOL_BX = "BX"
    SCHOOL_CHOICES = (
        (SCHOOL_BB, "博白"),
        (SCHOOL_BX, "博学")
    )
    school = models.CharField(max_length=2, choices=SCHOOL_CHOICES)
    is_temp = models.BooleanField()
    grade_idx = models.SmallIntegerField(choices=Choices.GRADE_CHOICES)
    class_idx = models.SmallIntegerField()

    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    enroll_year = models.IntegerField()


class Staff(models.Model):
    staff_id = models.IntegerField()
    name = models.CharField(max_length=6)
    gender = models.CharField(max_length=1, choices=Choices.GENDER_CHOICES)
    ethnicity = models.CharField(max_length=10)
    native_place = models.CharField(max_length=30, blank=True)
    political_status = models.CharField(max_length=2, choices=Choices.POLITICAL_CHOICES)
    enroll_time = models.DateTimeField()

    degree = models.CharField(max_length=4)
    grad_school = models.CharField(max_length=20)
    major = models.CharField(max_length=10)

    MARRIAGE_CHOICES = (
        ('Y', "已婚"),
        ('N', "未婚"),
        ('U', "未知")
    )
    married = models.CharField(max_length=1, choices=MARRIAGE_CHOICES)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    teaching_level = models.CharField(max_length=5, blank=True)
    teaching = models.CharField(max_length=10)
    admin_level = models.CharField(max_length=5, blank=True)
    department = models.ForeignKey("Department", blank=True, null=True)

# class Grade(models.Model):
#     name = models.CharField(max_length=5)
#
# class Class(models.Model):
#     pass


class Subject(models.Model):
    name = models.CharField(max_length=10)


class Department(models.Model):
    name = models.CharField(max_length=10)



