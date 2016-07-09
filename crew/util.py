from django.core import validators
from django.db import models, transaction
from datetime import date, datetime
import xlwt
import xlrd


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


class ImportModelError(Exception):
    pass


class FieldError(ImportModelError):
    def __init__(self, row, col_name, *args, **kwargs):
        self.row, self.col_name = row, col_name
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "行{row}, {col_name} {msg}".format(row=self.row, col_name=self.col_name,
                                               msg=super().__str__())

class UniqueError(ImportModelError):
    pass


def to_representation(obj, field):
    value = getattr(obj, field.name)
    style = None
    if isinstance(field, models.DateField):
        style = xlwt.easyxf(num_format_str='YYYY-MM-DD')
    if len(field.choices) > 0:
        for ch in field.choices:
            if ch[0] == value:
                return ch[1], style
        raise Exception(field.name + " " + str(value) + "Not found")
    return value, style


def to_value(row, col_name, rep, field, wb):
    if len(field.choices) > 0:
        for ch in field.choices:
            if ch[1] == rep:
                return ch[0]
        raise FieldError(row, col_name, "取值不合法:{0}".format(rep))

    if isinstance(field, models.DateField):
        try:
            year, month, day, *_ = xlrd.xldate_as_tuple(rep, wb.datemode)
            return date(year, month, day)
        except:
            raise FieldError(row, col_name, "日期格式错误: {0}".format(rep))

    if isinstance(field, models.IntegerField) or isinstance(field, models.AutoField):
        try:
            return int(rep)
        except:
            raise FieldError(row, col_name, "不是整数: {0}".format(rep))

    return rep


def export_model(query_set, model_class):
    wb = xlwt.Workbook()
    ws = wb.add_sheet("学生信息")

    fields = model_class._meta.fields
    columns = [field.verbose_name for field in fields]
    for j, c in enumerate(columns):
        ws.write(0, j, c)
    for i, obj in enumerate(query_set):
        representations = [to_representation(obj, field) for field in fields]
        for j, (rep, style) in enumerate(representations):
            if style:
                ws.write(i + 1, j, rep, style)
            else:
                ws.write(i + 1, j, rep)
    wb.save("学生.xls")


def import_model(file, model_class):
    fields = model_class._meta.fields
    columns = [field.verbose_name for field in fields]
    print(columns)

    try:
        wb = xlrd.open_workbook(file_contents=file.read())
        ws = wb.sheet_by_index(0)
    except:
        raise ImportModelError("无法打开文件")

    header = ws.row_values(0)

    column_indices = [header.index(column) if column in header else None for column in columns]
    not_found = [column for column, index in zip(columns, column_indices) if index is None]
    if not_found:
        raise ImportModelError("缺少以下列: " + ','.join(not_found))

    students = []
    for row_index in range(1, ws.nrows):
        row = ws.row_values(row_index)
        kwargs = {}
        for field, index in zip(fields, column_indices):
            kwargs[field.name] = to_value(row_index, field.verbose_name, row[index], field, wb)

        s = model_class(**kwargs)
        print(s)
        print(kwargs)
        s.full_clean()
        students.append(s)

    return students
