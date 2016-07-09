from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError

from crispy_forms.utils import render_crispy_form
from django.core.context_processors import csrf
from django.http.response import HttpResponse
from crew import util
import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, generics
from .serializers import DepartmentSerializer, StudentSerializer, PersonSerializer
from .models import Department, Student, Person
from .forms import *
import csv
import xlrd


# Create your views here.

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = json.dumps(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def query(request):
    ctx = {"form": QueryForm()}
    return render(request, "crew/query.html", ctx)


@login_required
@require_http_methods(['GET'])
@csrf_exempt
def student_list(request):
    page_index = int(request.GET.get('page', 1))
    action = request.GET.get('action', 'list')
    query_form = QueryForm(request.GET)
    if query_form.is_valid():
        if action == 'list':
            students = Paginator(query_form.get_query_set(), 1).page(page_index)
            form_html = render_crispy_form(query_form)
            content_html = render_to_string("crew/components/student_list.html", {"students": students})
            return JSONResponse(data={"ok": True, "form_html": form_html, "content_html": content_html})
        else:
            students = query_form.get_query_set()
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="student_info.csv"'
            writer = csv.writer(response)
            writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
            writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])
            return response

    form_html = render_crispy_form(query_form)
    return JSONResponse(data={"ok": False, "form_html": form_html})


@login_required
@require_http_methods(['GET', 'POST', 'DELETE'])
@csrf_exempt
def student_detail(request, pk):
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return JSONResponse(data={'ok': False, 'message': '找不到学生'})

    ok = True
    if request.method == 'DELETE':
        student.delete()
        return JSONResponse(data={'ok': True})
    elif request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
        else:
            ok = False
    else:
        form = StudentForm(instance=student)
    ctx = {'action': reverse('crew:student_detail', args=(pk,)), 'form': form}
    content_html = render_to_string("crew/components/student_detail.html", ctx, request=request)
    return JSONResponse(data={'ok': ok, 'content_html': content_html})


@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return JSONResponse(data={'ok': True})
    else:
        form = StudentForm()
    ctx = {'action': request.path, 'form': form}
    content_html = render_to_string("crew/components/student_detail.html", ctx, request=request)
    return JSONResponse(data={'ok': False, 'content_html': content_html})


@login_required
@csrf_exempt
def import_data(request):
    if request.method == 'GET':
        return render(request, 'crew/import.html')
    else:
        if not request.FILES:
            print("NO files")
        file = request.FILES['file']

        try:
            students = util.import_model(file, Student)
        except Exception as e:
            return JSONResponse(data={'ok': False, 'msg': str(e)})

        try:
            with transaction.atomic():
                for s in students:
                    s.save()
        except IntegrityError as e:
            return JSONResponse(data={'ok': False, 'msg': str(e)})
        return JSONResponse(data={'ok': True})
