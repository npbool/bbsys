from django.core import validators
from django.db import models
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


def to_value(rep, field, wb):
    if len(field.choices) > 0:
        for ch in field.choices:
            if ch[1] == rep:
                return ch[0]
        raise Exception(field.name + " " + str(rep) + "Not found")
    if isinstance(field, models.DateField):
        year, month, day, *_ = xlrd.xldate_as_tuple(rep, wb.datemode)
        return date(year, month, day)
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


def import_model(filename, model_class):
    fields = model_class._meta.fields
    columns = [field.verbose_name for field in fields]
    print(columns)

    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_index(0)
    header = ws.row_values(0)
    print(header)

    column_indices = [header.index(column) if column in header else None for column in columns]
    not_found = [column for column, index in zip(columns, column_indices) if index is None]
    if not_found:
        raise Exception("缺少以下列: "+','.join(not_found))

    kwargs = {}
    for row_index in range(1, ws.nrows):
        row = ws.row_values(row_index)
        for field, index in zip(fields, column_indices):
            kwargs[field.name] = to_value(row[index], field, wb)
        print(kwargs)
        s = model_class(**kwargs)
        s.save()

