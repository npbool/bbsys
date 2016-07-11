from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button, Div, Field, Fieldset, ButtonHolder
from crew.util import Choices
from crew import models


class BSForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BSForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 col-sm-4'
        self.helper.field_class = 'col-md-9 col-sm-8'
        self.helper.html5_required = True


class BSCol(Div):
    def __init__(self, *args, col, **kwargs):
        kwargs['css_class'] = kwargs.get('css_class', '') + ' col-md-{col} col-sm-{col}'.format(col=col)
        super(BSCol, self).__init__(*args, **kwargs)


class BSRow(Div):
    def __init__(self, *args, **kwargs):
        kwargs['css_class'] = kwargs.get('css_class', '') + ' row'
        super(BSRow, self).__init__(*args, **kwargs)


class QueryStudentForm(BSForm):
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
    school = forms.MultipleChoiceField(
        label="学校",
        choices=models.Student.SCHOOL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        initial=[s[0] for s in models.Student.SCHOOL_CHOICES]
    )
    prop = forms.MultipleChoiceField(
        label="类别",
        choices=models.Student.PROP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=[s[0] for s in models.Student.PROP_CHOICES]
    )
    category = forms.MultipleChoiceField(
        label="文理",
        choices=models.Student.CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        initial=[s[0] for s in models.Student.CATEGORY_CHOICES]
    )

    def __init__(self, *args, **kwargs):
        super(QueryStudentForm, self).__init__(*args, **kwargs)
        self.helper.form_id = "id-query-form"
        # self.helper.layout = Layout(
        #     'grade', 'class_', 'school', 'prop', 'category', 'student_id'
        # )

    def get_query_set(self):
        qs = models.Student.objects.all()
        filter_args = {}
        data = self.cleaned_data
        if data['grade']:
            filter_args['grade_idx'] = data['grade']
        if data['class_']:
            filter_args['class_idx'] = data['class_']
        if data['student_id']:
            filter_args['student_id'] = data['student_id']
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
        self.helper.form_class = 'form'
        self.helper.html5_required = True
        self.helper.layout = Layout(
            BSRow(
                BSCol('student_id', col=3),
                BSCol('name', col=2),
                BSCol('gender', col=2),
                BSCol('school', col=2),
                BSCol('prop', col=2),
            ),
            BSRow(
                BSCol('exam_id', col=3),
                BSCol('exam_id_alt', col=3),
                BSCol('national_id', col=5),
            ),
            BSRow(
                BSCol('enroll_year', col=2),
                BSCol('category', col=2),
                BSCol('grade_idx', col=2),
                BSCol('class_idx', col=2),
                BSCol('political_status', col=2)
            ),
            BSRow(
                BSCol('birth_date', col=3),
                BSCol('native_place', col=3),
                BSCol('ethnicity', col=2),
                BSCol('hukou_is_agri', col=2),
            ),
            BSRow(
                BSCol('address', col=7),
                BSCol('phone', col=3),
            ),
            ButtonHolder(
                Button("save", "保存", css_class="btn btn-primary", css_id="id-btn-save"),
                Button("return", "返回", css_class="btn btn-default", css_id="id-btn-back")
            )
        )

    class Meta:
        model = models.Student
        fields = '__all__'


class InputRecordForm(BSForm):
    semester = forms.ModelChoiceField(
        queryset=models.Semester.objects.all(),
        label="学期",
    )
    exam = forms.ModelChoiceField(
        queryset=models.Exam.objects.all(),
        label="考试"
    )
    subject = forms.ModelChoiceField(
        queryset=models.Subject.objects.all(),
        label="科目"
    )
    grade = forms.TypedChoiceField(
        label="年级",
        choices=Choices.GRADE_CHOICES,
        coerce=lambda x: int(x),
        initial=1,
        required=True
    )
    class_ = forms.IntegerField(
        label="班级",
        required=True,
        min_value=1,
        max_value=20
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_id = 'id-query-form'

    def clean(self):
        cleaned_data = super().clean()
        exam = cleaned_data['exam']
        subject = cleaned_data['subject']
        if not exam.subjects.filter(pk=subject.pk).exists():
            # raise forms.ValidationError("此次考试未考科目"+subject.name)
            self.add_error("subject", "此次考试未考科目" + subject.name)
