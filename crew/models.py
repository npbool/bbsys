# coding: utf8
from django.db import models
from .util import *
from django.core.validators import RegexValidator


# Create your models here.
class Student(models.Model):
    student_id = models.CharField(max_length=10, unique=True, validators=[RegexValidator(r'[A-Z]\d+', "学号格式错误")],
                                  verbose_name="学号")
    exam_id = models.CharField(max_length=20, blank=True, verbose_name="考号")
    # exam_id_alt = models.CharField(max_length=10, blank=True, verbose_name="考号2")
    national_id = models.CharField(max_length=18, unique=True, verbose_name="身份证号")
    name = models.CharField(max_length=6, verbose_name="姓名")
    gender = models.CharField(max_length=1, choices=Choices.GENDER_CHOICES, verbose_name="性别")

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
    prop = models.CharField(max_length=1, choices=PROP_CHOICES, verbose_name="学生类别")

    grade_idx = models.SmallIntegerField(choices=Choices.GRADE_CHOICES, verbose_name="年级")
    class_idx = models.SmallIntegerField(verbose_name="班号")
    CATEGORY_CHOICES = (
        ('W', "文科"),
        ('L', "理科"),
        ('U', "未分科")
    )
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, verbose_name="文理状态")
    enroll_year = models.IntegerField(verbose_name="入学年份(四位)")

    def __str__(self):
        return self.name + "_" + self.get_school_display() + "_" + self.get_grade_idx_display() + "_" + str(
            self.class_idx)


class Staff(models.Model):
    staff_id = models.IntegerField()
    name = models.CharField(max_length=6)
    gender = models.CharField(max_length=1, choices=Choices.GENDER_CHOICES)

    phone = models.CharField(max_length=15, validators=[phone_validator])
    department = models.ForeignKey("Department", blank=True, null=True)
    teaching_grade = models.IntegerField(choices=Choices.GRADE_CHOICES)
    teaching_subject = models.ForeignKey("Subject")


class Subject(models.Model):
    name = models.CharField(max_length=10, verbose_name="科目")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "科目"
        verbose_name_plural = verbose_name


class Exam(models.Model):
    name = models.CharField(max_length=20, verbose_name="考试名称")
    subjects = models.ManyToManyField("Subject", verbose_name="包含科目")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "考试"
        verbose_name_plural = verbose_name


class Semester(models.Model):
    SEASON_CHOICES = (
        (0, "上学期"),
        (1, "下学期")
    )
    year = models.IntegerField(verbose_name="年份")
    season = models.IntegerField(verbose_name="学期", choices=SEASON_CHOICES)

    def __str__(self):
        return "{0}{1}".format(self.year, "上下"[self.season])

    class Meta:
        verbose_name = "学期"
        verbose_name_plural = verbose_name


class Record(models.Model):
    subject = models.ForeignKey("Subject", verbose_name="科目")
    student = models.ForeignKey("Student", verbose_name="学生")
    semester = models.ForeignKey("Semester", verbose_name="学期")
    exam = models.ForeignKey("Exam", verbose_name="考试")
    score = models.FloatField(verbose_name="成绩")

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.subject, self.semester, self.student, self.score)

    class Meta:
        verbose_name = "成绩"
        verbose_name_plural = verbose_name


class Department(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return str(self.pk) + ": " + self.name


class Person(models.Model):
    name = models.CharField(max_length=10)
    dept = models.ForeignKey(Department)
    grade = models.IntegerField(choices=Choices.GRADE_CHOICES)
