# coding: utf8
from django.db import models
from .util import *
from django.core.validators import RegexValidator


# Create your models here.
class Student(models.Model):
    student_id = models.CharField(max_length=7, unique=True)
    exam_id = models.CharField(max_length=10, unique=True, blank=True,
                               validators=[RegexValidator(r'\d{10}', "考号必须为10位数字")])
    exam_id_alt = models.CharField(max_length=10, unique=True, blank=True,
                                   validators=[RegexValidator(r'\d{10}', "考号必须为10位数字")])
    national_id = models.CharField(max_length=18, unique=True)
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
    PROP_CHOICES = (
        ('Y', "应届生"),
        ('W', "往届生")
    )
    prop = models.CharField(max_length=1, choices=PROP_CHOICES)

    grade_idx = models.SmallIntegerField(choices=Choices.GRADE_CHOICES)
    class_idx = models.SmallIntegerField()
    CATEGORY_CHOICES = (
        ('W', "文科"),
        ('L', "理科"),
        ('U', "未分科")
    )
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)

    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    enroll_year = models.IntegerField()

    def __str__(self):
        return self.name + "_" + self.get_school_display() + "_" + self.get_grade_idx_display() + "_" + str(
            self.class_idx)


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


class Subject(models.Model):
    name = models.CharField(max_length=10)


class Department(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return str(self.pk) + ": " + self.name


class Person(models.Model):
    name = models.CharField(max_length=10)
    dept = models.ForeignKey(Department)
    grade = models.IntegerField(choices=Choices.GRADE_CHOICES)
