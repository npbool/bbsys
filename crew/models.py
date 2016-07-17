# coding: utf8
from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator


class Choices:
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女')
    )
    POLITICAL_CHOICES = (
        ('DY', "中共党员"),
        ('TY', "共青团员"),
        ('QZ', "群众")
    )

    SCHOOL_BB = "BB"
    SCHOOL_BX = "BX"
    SCHOOL_CHOICES = (
        (SCHOOL_BB, "博白(0646)"),
        (SCHOOL_BX, "博学(0657)")
    )

    GRADE_S1 = 1
    GRADE_S2 = 2
    GRADE_S3 = 3
    GRADE_J1 = -1
    GRADE_J2 = -2
    GRADE_J3 = -3
    GRADE_CHOICES = (
        (GRADE_S1, "高一年级"),
        (GRADE_S3, "高二年级"),
        (GRADE_S3, "高三年级"),
        (GRADE_J1, "初一年级"),
        (GRADE_J2, "初二年级"),
        (GRADE_J3, "初三年级")
    )

    HUKOU_CHOICES = (
        (0, "非农业户口"),
        (1, "农业户口")
    )

    @staticmethod
    def display_to_value(display, choices):
        for v, d in choices:
            if d == display:
                return v
        raise ValueError(display + " is not a valid display value")


class SegmentsField(models.CharField):
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        if value == '':
            return []
        return sorted([int(x) for x in value.split(',')], reverse=True)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is None:
            return value
        return sorted([int(x) for x in value.split(',')], reverse=True)

    def get_prep_value(self, value):
        return ','.join(str(x) for x in value)

    def get_db_prep_value(self, value, connection, prepared=False):
        return ','.join(str(x) for x in value)


phone_validator = RegexValidator(r"[\d|-]+", message="号码格式错误")


# Create your models here.
class Student(models.Model):
    student_id = models.CharField(max_length=10, unique=True, validators=[RegexValidator(r'[A-Z]\d+', "学号格式错误")],
                                  verbose_name="学号")
    exam_id = models.CharField(max_length=20, blank=True, verbose_name="考号")
    # exam_id_alt = models.CharField(max_length=10, blank=True, verbose_name="考号2")
    national_id = models.CharField(max_length=18, unique=True, verbose_name="身份证号")
    name = models.CharField(max_length=6, verbose_name="姓名")
    gender = models.CharField(max_length=1, choices=Choices.GENDER_CHOICES, verbose_name="性别")

    school = models.CharField(max_length=2, choices=Choices.SCHOOL_CHOICES, verbose_name="学校")
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

    class Meta:
        verbose_name_plural = verbose_name = "学生"


class Staff(models.Model):
    staff_id = models.IntegerField()
    name = models.CharField(max_length=6)
    gender = models.CharField(max_length=1, choices=Choices.GENDER_CHOICES)

    phone = models.CharField(max_length=15, validators=[phone_validator])
    department = models.ForeignKey("Department", blank=True, null=True)
    teaching_subject = models.ForeignKey("Subject")

    def __str__(self):
        return "{staff_id} {name} - {teaching_subject} - {dept}".format(staff_id=self.staff_id, name=self.name,
                                                                        teaching_subject=self.teaching_subject,
                                                                        dept=self.department)

    class Meta:
        verbose_name = verbose_name_plural = "职工"


class Subject(models.Model):
    name = models.CharField(max_length=10, verbose_name="科目", unique=True)
    belong_science = models.BooleanField(verbose_name="理科是否统计", default=False)
    belong_art = models.BooleanField(verbose_name="文科是否统计", default=False)
    belong_universal = models.BooleanField(verbose_name="不分科是否统计", default=False)
    total_score = models.IntegerField(verbose_name="满分")
    segments = models.CommaSeparatedIntegerField(verbose_name="分数段", default=[], max_length=1024)

    ratio_validators = [MaxValueValidator(1, "比例不能超过1"), MinValueValidator(0, "比例不能小于0")]
    excellent_ratio = models.FloatField(verbose_name="优比例", default=0.9, validators=ratio_validators)
    good_ratio = models.FloatField(verbose_name="良比例", default=0.8, validators=ratio_validators)
    pass_ratio = models.FloatField(verbose_name="及格比例", default=0.6, validators=ratio_validators)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "科目"
        verbose_name_plural = verbose_name

    @staticmethod
    def science_total():
        return Subject.objects.filter(belong_science=True).aggregate(models.Sum('total_score'))

    @staticmethod
    def art_total():
        return Subject.objects.filter(belong_art=True).aggregate(models.Sum('total_score'))

    @staticmethod
    def universal_total():
        return Subject.objects.filter(belong_universal=True).aggregate(models.Sum('total_score'))

    @staticmethod
    def category_subjects(category):
        if category == 'W':
            return Subject.objects.filter(belong_art=True)
        elif category == 'L':
            return Subject.objects.filter(belong_science=True)
        elif category == 'U':
            return Subject.objects.filter(belong_universal=True)
        else:
            raise ValueError("category illegal")


class ClassTeacher(models.Model):
    school = models.CharField(max_length=2, choices=Choices.SCHOOL_CHOICES, verbose_name="学校")
    grade_idx = models.IntegerField(choices=Choices.GRADE_CHOICES, verbose_name="年级")
    class_idx = models.IntegerField(verbose_name="班级")
    subject = models.ForeignKey('Subject', null=True, blank=True)
    teacher = models.ForeignKey('Staff')

    class Meta:
        unique_together = ('school', 'grade_idx', 'class_idx', 'subject')
        verbose_name = verbose_name_plural = "任课教师/班主任"

    def __str__(self):
        return "{role} {school} {grade}{class_idx} {teacher}".format(
            role="班主任" if self.subject is None else self.subject.name,
            school=self.get_school_display(),
            grade=self.get_grade_idx_display(),
            class_idx=self.class_idx,
            teacher=self.teacher.name
        )

    @classmethod
    def get_teacher(cls, school_display, grade_display, class_idx, subject):
        try:
            school = Choices.display_to_value(school_display, Choices.SCHOOL_CHOICES)
            grade_idx = Choices.display_to_value(grade_display, Choices.GRADE_CHOICES)
            return cls.objects.get(school=school, grade_idx=grade_idx, class_idx=class_idx, subject=subject)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_manager(cls, school_display, grade_display, class_idx):
        return cls.get_teacher(school_display, grade_display, class_idx, None)


class Leader(models.Model):
    school = models.CharField(max_length=2, choices=Choices.SCHOOL_CHOICES, verbose_name="学校")
    grade_idx = models.IntegerField(choices=Choices.GRADE_CHOICES, verbose_name="年级")
    teacher = models.ForeignKey('Staff')

    class Meta:
        verbose_name_plural = verbose_name = "教研组长"


class SubjectLeader(models.Model):
    school = models.CharField(max_length=2, choices=Choices.SCHOOL_CHOICES, verbose_name="学校")
    grade_idx = models.IntegerField(choices=Choices.GRADE_CHOICES, verbose_name="年级")
    subject = models.ForeignKey('Subject')
    teacher = models.ForeignKey('Staff')

    class Meta:
        verbose_name_plural = verbose_name = "备课组长"


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
        unique_together = ('year', 'season')


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
        unique_together = ('subject', 'student', 'semester', 'exam')


class Department(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return str(self.pk) + ": " + self.name

    class Meta:
        verbose_name_plural = verbose_name = "部门"


class SystemSettings(models.Model):
    default_semester = models.ForeignKey(Semester)
    default_exam = models.ForeignKey(Exam)
    science_segments = models.CommaSeparatedIntegerField(max_length=1024, verbose_name="理科分数段")
    art_segments = models.CommaSeparatedIntegerField(max_length=1024, verbose_name="文科分数段")
    universal_segments = models.CommaSeparatedIntegerField(max_length=1024, verbose_name="不分科分数段")

    @staticmethod
    def get_instance():
        return SystemSettings.objects.first()

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = verbose_name


class Person(models.Model):
    name = models.CharField(max_length=10)
    dept = models.ForeignKey(Department)
    grade = models.IntegerField(choices=Choices.GRADE_CHOICES)
