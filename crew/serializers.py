from rest_framework import serializers
from .models import *
from .util import *


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department


class PersonSerializer(serializers.ModelSerializer):
    grade = serializers.ChoiceField(html_cutoff=6, choices=Choices.GRADE_CHOICES)
    class Meta:
        model = Person
