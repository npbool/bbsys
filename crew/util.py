from django.core import validators
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

    GRADE_S1 = 1
    GRADE_S2 = 2
    GRADE_S3 = 3
    GRADE_J1 = -1
    GRADE_J2 = -2
    GRADE_J3 = -3
    GRADE_CHOICES = (
        (GRADE_S1, "高一"),
        (GRADE_S3, "高二"),
        (GRADE_S3, "高三"),
        (GRADE_J1, "初一"),
        (GRADE_J2, "初二"),
        (GRADE_J3, "初三")
    )

    HUKOU_CHOICES = (
        (0, "非农业户口"),
        (1, "农业户口")
    )


phone_validator = validators.RegexValidator(r"[\d|-]+", message="号码格式错误")
