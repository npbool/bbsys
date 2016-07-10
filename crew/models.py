# coding: utf8
from django.db import models
from .util import *
from django.core.validators import RegexValidator


# Create your models here.
class Student(models.Model):
    student_id = models.CharField(max_length=7, unique=True, validators=[RegexValidator(r'[A-Z]\d+', "学号格式错误")],
                                  verbose_name="学号")
    exam_id = models.CharField(max_length=10, blank=True, verbose_name="考号1")
    exam_id_alt = models.CharField(max_length=10, blank=True, verbose_name="考号2")
    national_id = models.CharField(max_length=18, unique=True, verbose_name="身份证号")
    name = models.CharField(max_length=6, verbose_name="姓名")
    gender = models.CharField(max_length=1, choices=Choices.GENDER_CHOICES, verbose_name="性别")
    birth_date = models.DateField(verbose_name="出生日期")

    ethnicity = models.CharField(max_length=10, verbose_name="民族")
    native_place = models.CharField(max_length=30, verbose_name="籍贯")
    political_status = models.CharField(max_length=2, choices=Choices.POLITICAL_CHOICES, verbose_name="政治面貌")

    hukou_is_agri = models.BooleanField(choices=Choices.HUKOU_CHOICES, verbose_name="户口")

    SCHOOL_BB = "BB"
    SCHOOL_BX = "BX"
    SCHOOL_CHOICES = (
        (SCHOOL_BB, "博白(0646)"),
        (SCHOOL_BX, "博学(0657)")
    )
    school = models.CharField(max_length=2, choices=SCHOOL_CHOICES, verbose_name="学校")
    PROP_CHOICES = (
        ('Y', "应届生"),
        ('W', "往届生")
    )
    prop = models.CharField(max_length=1, choices=PROP_CHOICES, verbose_name="是否应届")

    grade_idx = models.SmallIntegerField(choices=Choices.GRADE_CHOICES, verbose_name="年级")
    class_idx = models.SmallIntegerField(verbose_name="班号")
    CATEGORY_CHOICES = (
        ('W', "文科"),
        ('L', "理科"),
        ('U', "未分科")
    )
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, verbose_name="文理状态")

    address = models.CharField(max_length=50, verbose_name="地址")
    phone = models.CharField(max_length=15, validators=[phone_validator], verbose_name="手机号")
    enroll_year = models.IntegerField(verbose_name="入学年份(四位)")

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
    name = models.CharField(max_length=10, verbose_name="科目")

    def __str__(self):
        return self.name


class Exam(models.Model):
    name = models.CharField(max_length=20, verbose_name="考试名称")

    def __str__(self):
        return self.name


class Semester(models.Model):
    SEASON_CHOICES = (
        (0, "上学期"),
        (1, "下学期")
    )
    year = models.IntegerField(verbose_name="年份")
    season = models.IntegerField(verbose_name="学期", choices=SEASON_CHOICES)

    def __str__(self):
        return "{0}{1}".format(self.year, "上下"[self.season])


class Record(models.Model):
    subject = models.ForeignKey("Subject", verbose_name="科目")
    student = models.ForeignKey("Student", verbose_name="学生")
    semester = models.ForeignKey("Semester", verbose_name="学期")
    score = models.FloatField(verbose_name="成绩")

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.subject, self.semester, self.student, self.score)


class Department(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return str(self.pk) + ": " + self.name


class Person(models.Model):
    name = models.CharField(max_length=10)
    dept = models.ForeignKey(Department)
    grade = models.IntegerField(choices=Choices.GRADE_CHOICES)
