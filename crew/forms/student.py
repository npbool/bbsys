from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button, Div, Field, Fieldset, ButtonHolder
from crew.models import Student, Exam, Subject, Record, Semester, Choices, SystemSettings

class BSCol(Div):
    def __init__(self, *args, col, **kwargs):
        kwargs['css_class'] = kwargs.get('css_class', '') + ' col-md-{col} col-sm-{col}'.format(col=col)
        super(BSCol, self).__init__(*args, **kwargs)


class BSRow(Div):
    def __init__(self, *args, **kwargs):
        kwargs['css_class'] = kwargs.get('css_class', '') + ' row'
        super(BSRow, self).__init__(*args, **kwargs)


class QueryStudentForm(forms.Form):
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
    student_id = forms.CharField(
        label="学号",
        required=False,
    )
    name = forms.CharField(
        label="姓名",
        required=False
    )
    school = forms.MultipleChoiceField(
        label="学校",
        choices=Choices.SCHOOL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=[s[0] for s in Choices.SCHOOL_CHOICES]
    )
    prop = forms.MultipleChoiceField(
        label="类别",
        choices=Student.PROP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=[s[0] for s in Student.PROP_CHOICES]
    )
    category = forms.MultipleChoiceField(
        label="文理",
        choices=Student.CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=[s[0] for s in Student.CATEGORY_CHOICES]
    )

    def __init__(self, *args, **kwargs):
        super(QueryStudentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "id-query-form"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 col-sm-4'
        self.helper.field_class = 'col-md-9 col-sm-8'
        self.helper.html5_required = True

    def get_query_set(self):
        qs = Student.objects.all()
        filter_args = {}
        data = self.cleaned_data
        if data['grade']:
            filter_args['grade_idx'] = data['grade']
        if data['class_']:
            filter_args['class_idx'] = data['class_']
        if data['student_id']:
            filter_args['student_id'] = data['student_id']
        if data['name']:
            filter_args['name'] = data['name']
        filter_args['school__in'] = data['school']
        filter_args['prop__in'] = data['prop']
        filter_args['category__in'] = data['category']
        return qs.filter(**filter_args)


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'id-student-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4 col-sm-4'
        self.helper.field_class = 'col-md-8 col-sm-8'
        self.helper.html5_required = True
        self.helper.layout = Layout(
            BSRow(
                BSCol('student_id', col=4),
                BSCol('name', col=4),
                BSCol('gender', col=4),
            ),
            BSRow(
                BSCol('school', col=4),
                BSCol('prop', col=8),
            ),
            BSRow(
                BSCol('grade_idx', col=6),
                BSCol('class_idx', col=6),
            ),

            BSRow(
                BSCol('exam_id', col=6),
                BSCol('national_id', col=6),
            ),
            BSRow(
                BSCol('enroll_year', col=6),
                BSCol('category', col=6),
            ),
            ButtonHolder(
                Button("save", "保存", css_class="btn btn-primary", css_id="id-btn-save"),
                Button("return", "返回", css_class="btn btn-default", css_id="id-btn-back")
            )
        )

    class Meta:
        model = Student
        fields = '__all__'


