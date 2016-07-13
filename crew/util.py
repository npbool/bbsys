from django.core import validators
from django.db import models, transaction
from django.http.response import HttpResponse
from django.conf import settings
from crew.models import Student, Record, Subject, Exam
import json
from datetime import date, datetime
import xlwt
import xlrd


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = json.dumps(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


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

    if isinstance(field, models.IntegerField):
        try:
            return int(rep)
        except:
            raise FieldError(row, col_name, "不是整数: {0}".format(rep))

    if isinstance(field, models.AutoField):
        if rep == '':
            return None
        try:
            return int(rep)
        except:
            raise FieldError(row, col_name, "必须留空或取整数")
    if isinstance(field, models.CharField):
        if isinstance(rep, float):
            raise FieldError(row, col_name, "必须选择文字格式")
        return str(rep)
    return rep


def export_student(file, query_set):
    wb = xlwt.Workbook()
    ws = wb.add_sheet("学生信息")

    fields = Student._meta.fields
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
    wb.save(file)


def import_student(file):
    fields = Student._meta.fields
    columns = [field.verbose_name for field in fields]
    debug_print(columns)

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

        s = Student(**kwargs)
        debug_print(s)
        debug_print(kwargs)
        s.clean()
        students.append(s)

    return students


def get_subject_id_list(exam, subject_list):
    m = {s.name: s.pk for s in exam.subjects.all()}
    try:
        res = [m[s] for s in subject_list]
        return res
    except:
        raise ImportModelError("科目与考试不匹配")


def import_record(file, exam, semester):
    try:
        wb = xlrd.open_workbook(file_contents=file.read())
        ws = wb.sheet_by_index(0)
    except:
        raise ImportModelError("无法打开文件")
    header = ws.row_values(0)
    if "考号" not in header:
        raise ImportModelError("缺少考号")

    subjects = [sub for sub in header if sub != '考号' and sub != '姓名']
    debug_print(subjects)
    subject_col_list = [col for col, sub in enumerate(header) if sub != '考号' and sub != '姓名']
    debug_print(subject_col_list)
    subject_id_list = get_subject_id_list(exam, subjects)
    debug_print(subject_id_list)
    if len(subjects) != len(set(subjects)):
        raise ImportModelError("科目有重复")

    exam_id_col = header.index("考号")
    exam_id_list = ws.col_values(exam_id_col, 1)
    if len(exam_id_list) != len(set(exam_id_list)):
        raise ImportModelError("考号有重复")

    table = {}
    for row in range(1, ws.nrows):
        exam_id = ws.cell_value(row, exam_id_col)
        if isinstance(exam_id, float):
            raise ImportModelError("考号必须为文本格式")
        for col, subject_id in zip(subject_col_list, subject_id_list):
            value = ws.cell_value(row, col)
            if value != '':
                table[(exam_id, subject_id)] = value

    records = Record.objects.filter(exam=exam, semester=semester, student__exam_id__in=exam_id_list,
                                    subject_id__in=subject_id_list).select_related(
        "student")
    for record in records:
        table_key = (record.student.exam_id, record.subject_id)
        if table_key not in table:
            record.delete()
        else:
            record.score = table[table_key]
            record.save()
            del table[table_key]
    for (exam_id, subject_id) in table:
        try:
            student = Student.objects.get(exam_id=exam_id)
        except Student.DoesNotExist:
            raise ImportModelError("考号{0}无对应学生".format(exam_id))
        Record.objects.create(subject_id=subject_id, student=student, exam=exam, semester=semester,
                              score=table[(exam_id, subject_id)])


def import_record_wrapper(file, exam, semester):
    with transaction.atomic():
        import_record(file, exam, semester)


def debug_print(*args, **kwargs):
    if settings.DEBUG:
        print(*args, **kwargs)
