from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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
    return render(request, "crew/query.html", {"form": QueryForm()})

@login_required
@require_http_methods(['GET', 'POST'])
@csrf_exempt
def student_list(request):
    if request.method == 'POST':
        query_form = QueryForm(request.POST)
        if query_form.is_valid():
            form_html = render_crispy_form(query_form)
            return JSONResponse(data={"ok": True, "data_html": "<p>succ</p>", "form_html": form_html})
    else:
        query_form = QueryForm()
    form_html = render_crispy_form(query_form)
    return JSONResponse(data={"ok": False, "form_html": form_html})


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
