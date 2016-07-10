from django.shortcuts import render
from crew.forms import QueryRecordForm


def record_query(request):
    return render(request, "record/query.html", {'form': QueryRecordForm()})


def record_list(request):
    return ""
