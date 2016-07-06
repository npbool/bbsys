from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button
from crew.util import Choices
from crew import models


class BSForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BSForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-query-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.html5_required = True


class QueryForm(BSForm):
    grade = forms.TypedChoiceField(
        label="年级",
        choices=Choices.GRADE_CHOICES,
        coerce=lambda x: int(x),
        initial=1,
        required=False
    )
    class_ = forms.IntegerField(
        label="班级",
        required=False,
        min_value=1,
        max_value=20
    )
    school = forms.MultipleChoiceField(
        label="学校",
        choices=models.Student.SCHOOL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    prop = forms.MultipleChoiceField(
        label="类别",
        choices=models.Student.PROP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super(QueryForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'grade', 'class_', 'school', 'prop',
        )

    def get_query_set(self):
        qs = models.Student.objects.all()
        filter_args = {}
        data = self.cleaned_data
        if data['grade']:
            filter_args['grade_idx'] = data['grade']
        if data['class_']:
            filter_args['class_idx'] = data['class_']
        filter_args['school__in'] = data['school']
        filter_args['prop__in'] = data['prop']
        return qs.filter(**filter_args)


class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = '__all__'
