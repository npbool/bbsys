from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from crispy_forms.utils import render_crispy_form
from django.core.context_processors import csrf
from django.http.response import HttpResponse
import json
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import mixins, generics
from .serializers import DepartmentSerializer, StudentSerializer, PersonSerializer
from .models import Department, Student, Person
from .forms import *


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
@require_http_methods(['GET', 'POST'])
@csrf_exempt
def student_list(request):
    if request.method == 'POST':
        print(request.POST)
        page_index = request.POST.get('page', 1)
        query_form = QueryForm(request.POST)
        if query_form.is_valid():
            students = Paginator(query_form.get_query_set(), 1).page(page_index)
            form_html = render_crispy_form(query_form)
            content_html = render_to_string("crew/components/student_list.html", {"students": students})
            return JSONResponse(data={"ok": True, "form_html": form_html, "content_html": content_html})
    else:
        query_form = QueryForm()
    form_html = render_crispy_form(query_form)
    return JSONResponse(data={"ok": False, "form_html": form_html})


@login_required
@require_http_methods(['GET', 'POST'])
def student_detail(request, pk):
    try:
        student = Student.objects.get(pk=int(pk))
    except Student.DoesNotExist:
        return JSONResponse(data={'ok': False, 'message': '找不到学生'})

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return JSONResponse(data={'ok': True})

    form = StudentForm(instance=student)
    content_html = render_to_string("crew/components/student_detail.html", {'form': form})
    return JSONResponse(data={'ok': True, 'content_html': content_html})


class DepartmentList(generics.ListCreateAPIView):
    def get_queryset(self, *args, **kwargs):
        return Department.objects.filter(*args, **kwargs)

    serializer_class = DepartmentSerializer


class DepartmentDetail(generics.RetrieveUpdateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class StudentList(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class PersonList(generics.ListCreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class PersonDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
