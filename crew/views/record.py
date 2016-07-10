from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from crew.forms import QueryRecordForm
from crew.models import *
from crew.util import JSONResponse
from crispy_forms.utils import render_crispy_form


def record_query(request):
    return render(request, "record/query.html", {'form': QueryRecordForm()})


@require_GET
@csrf_exempt
def record_list(request):
    form = QueryRecordForm(request.GET)
    if not form.is_valid():
        return JSONResponse({
            'ok': False,
            'form_html': render_crispy_form(form)
        })

    editable = ('edit' in request.GET)
    students = Student.objects.filter(grade_idx=form.cleaned_data['grade'], class_idx=form.cleaned_data['class_'])
    exam = form.cleaned_data['exam']
    subjects = exam.subjects.all()
    records = Record.objects.filter(student__in=students, exam=exam)

    student_to_row = {s.pk: i for i, s in enumerate(students)}
    subject_to_col = {s.pk: j for j, s in enumerate(subjects)}
    record_table = [[""] * len(subjects) for _ in range(len(students))]
    for rec in records:
        row = student_to_row[rec.student_id]
        col = subject_to_col[rec.subject_id]
        record_table[row][col] = rec.score
    context = {
        'subjects': subjects,
        'data': [
            {'student': student,
             'records': [{'score': score, 'subject_id': sub.id} for score, sub in zip(records, subjects)],
             'total': sum(r for r in records if not isinstance(r, str))}
            for student, records in zip(students, record_table)
            ],
        'editable': True if editable == 1 else False
    }
    return JSONResponse({
        'ok': True,
        'content_html': render_to_string("record/components/record_list.html", context),
        'form_html': render_crispy_form(form)
    })
