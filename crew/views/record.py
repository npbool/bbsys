from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.core.paginator import Paginator
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q
from crew.forms import *
from crew.models import *
from crew.util import JSONResponse, debug_print
from crispy_forms.utils import render_crispy_form
from crew import analysis
import json
import functools
import operator

'''
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
'''


def record_query(request):
    return render(request, "record/input.html", {'form': InputRecordForm()})


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def record_input(request):
    page_no = int(request.GET.get('page', 1))
    if request.method == 'GET':
        form = InputRecordForm(request.GET)
        if not form.is_valid():
            return JSONResponse({
                'ok': False,
                'form_html': render_crispy_form(form)
            })
        semester = form.cleaned_data['semester']
        exam = form.cleaned_data['exam']
        subject = form.cleaned_data['subject']
        students_all = Student.objects.filter(grade_idx=form.cleaned_data['grade'],
                                              class_idx=form.cleaned_data['class_'])
        page = Paginator(students_all, 10).page(page_no)
        students = page.object_list

        records = Record.objects.filter(semester=semester, subject=subject, exam=exam, student__in=students)
        scores = {r.student_id: r.score for r in records}
        context = {
            'records': [
                {'student': student, 'score': scores[student.pk] if student.pk in scores else ''} for student in
                students
                ],
            'subject': subject, 'exam': exam, 'semester': semester, 'page': page,
        }
        content_html = render_to_string("record/components/record_input.html", context)
        form_html = render_crispy_form(form)
        return JSONResponse({
            'ok': True,
            'content_html': content_html,
            'form_html': form_html,
        })
    else:
        form = InputRecordForm(request.POST)
        if not form.is_valid():
            return JSONResponse({'ok': False, 'msg': "表单错误"})
        data = json.loads(request.POST['data'])
        print(data)
        updated_student = {d['student_id']: d['score'] for d in data}

        semester = form.cleaned_data['semester']
        exam = form.cleaned_data['exam']
        subject = form.cleaned_data['subject']
        records = Record.objects.filter(semester=semester, student__grade_idx=form.cleaned_data['grade'],
                                        subject=subject, exam=exam,
                                        student__class_idx=form.cleaned_data['class_'],
                                        student_id__in=updated_student.keys())
        try:
            with transaction.atomic():
                for record in records:
                    new_score = updated_student[record.student_id]
                    if new_score == '':
                        record.delete()
                    else:
                        record.score = float(new_score)
                        record.save()
                    del updated_student[record.student_id]
                for student_id in updated_student:
                    if updated_student[student_id] != '':
                        Record.objects.create(
                            semester=semester, subject=subject, exam=exam,
                            student_id=student_id, score=float(updated_student[student_id])
                        )
        except IntegrityError:
            return JSONResponse({'ok': False, 'msg': "数据不一致"})
        except ValueError:
            return JSONResponse({'ok': False, 'msg': "分数格式错误"})
        return JSONResponse({'ok': True})


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def record_import(request):
    pass


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def record_analysis(request):
    form = AnalyzeRecordForm()
    return render(request, 'record/analysis.html', {'form': form})


@require_GET
def api_record_analysis(request):
    form = AnalyzeRecordForm(request.GET)
    if form.is_valid():
        sort_by = request.GET['sort_by']
        ascending = int(request.GET['ascending']) == 1
        debug_print(sort_by, ascending)
        tp = form.cleaned_data['analysis_type']
        try:
            if tp == AnalyzeRecordForm.ANALYSIS_RANK:
                debug_print("RANK")
                ana = analysis.RankAnalysis(form, sort_by, ascending)
            elif tp == AnalyzeRecordForm.ANALYSIS_REL:
                debug_print("CMP")
                ana = analysis.RankCmpAnalysis(form, sort_by, ascending)
            else:
                raise analysis.AnalysisError("未实现")
            context = ana.get_context()

            content_html = render_to_string(ana.template_name, context)
            return JSONResponse({
                'ok': True,
                'form_html': render_crispy_form(form),
                'content_html': content_html
            })

        except analysis.AnalysisError as e:
            return JSONResponse({'ok': False, 'form_html': render_crispy_form(form), 'msg': str(e)})
    else:
        debug_print("INVALID")
        return JSONResponse({
            'ok': False,
            'msg': '表单错误',
            'form_html': render_crispy_form(form)
        })


@require_http_methods(['GET', 'POST'])
def record_segment_analysis(request):
    if request.method == 'POST':
        form = AnalysisSegForm(request.POST)
        if form.is_valid():
            try:
                ana = analysis.SegmentAnalysis(form)
                df_list = ana.get_df_list()

                context = {
                    'form': form,
                    'data': [
                        (subject_name, df.to_dict('records'), agg.to_dict(), [int(x) for x in segments.split(',')]) for
                        (subject_name, df, agg, segments) in df_list
                        ],
                }
                return render(request, 'record/segment.html', context)
            except analysis.AnalysisError as e:
                return render(request, 'record/segment.html', {'error': str(e), 'form': form})
    else:
        form = AnalysisSegForm()
    return render(request, 'record/segment.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def record_average_analysis(request):
    if request.method == 'POST':
        form = AnalysisAvgForm(request.POST)
        if form.is_valid():
            try:
                ana = analysis.AverageAnalysis(form)
                df = ana.get_df()
                # print(df)
                context = {
                    'form': form,
                    'data': df.to_dict('records'),
                    'subjects': [s.name for s in ana.show_subjects]
                }
                print(context['data'])
                return render(request, 'record/average.html', context)
            except analysis.AnalysisError as e:
                print(e)
                return render(request, 'record/average.html', {'form': form, 'error': e})
    else:
        form = AnalysisAvgForm()
    return render(request, 'record/average.html', {'form': form})
