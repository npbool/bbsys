from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Button, Div, Field, Fieldset, ButtonHolder
from crew.models import Student, Exam, Subject, Record, Semester, Choices, SystemSettings


class InputRecordForm(forms.Form):
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        label="学期",
    )
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        label="考试"
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
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
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 col-sm-4'
        self.helper.field_class = 'col-md-9 col-sm-8'
        self.helper.html5_required = True
        self.helper.form_id = 'id-query-form'

    def clean(self):
        cleaned_data = super().clean()
        if 'exam' in cleaned_data and 'subject' in cleaned_data:
            exam = cleaned_data['exam']
            subject = cleaned_data['subject']
            if not exam.subjects.filter(pk=subject.pk).exists():
                # raise forms.ValidationError("此次考试未考科目"+subject.name)
                self.add_error("subject", "此次考试未考科目" + subject.name)
        return cleaned_data


class AnalyzeRecordForm(forms.Form):
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        label="学期",
        required=True
    )
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        label="考试",
        required=True
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        label="科目",
        required=True,
    )
    grade = forms.ChoiceField(
        choices=Choices.GRADE_CHOICES,
        label="年级",
        required=True,
    )
    school_props = forms.MultipleChoiceField(
        choices=(
            (school[0] + ' ' + prop[0], school[1] + prop[1]) for school in Choices.SCHOOL_CHOICES for prop in
            Student.PROP_CHOICES
        ),
        label="类型",
        required=True
    )

    ANALYSIS_RANK = 1
    ANALYSIS_REL = 2
    analysis_type = forms.TypedChoiceField(
        choices=(
            (ANALYSIS_RANK, "名次"),
            (ANALYSIS_REL, "进退")
        ),
        coerce=lambda x: int(x),
        label="分析"
    )

    semester_cmp = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        label="比较学期",
        required=False,
    )
    exam_cmp = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        label="比较考试",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(AnalyzeRecordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 col-sm-4'
        self.helper.field_class = 'col-md-9 col-sm-8'
        self.helper.html5_required = True

        all_classes = [r['class_idx'] for r in Student.objects.all().values('class_idx').distinct()]
        self.fields['classes'] = forms.MultipleChoiceField(
            choices=list(zip(all_classes, all_classes)),
            label="班级",
            initial=all_classes
        )
        self.fields['subjects'].initial = [s.pk for s in Subject.objects.all()]

        self.helper.layout = Layout(
            'semester', 'exam', 'grade', 'classes', 'subjects', 'school_props', 'analysis_type', 'semester_cmp',
            'exam_cmp'
        )
        self.helper.form_id = 'id-query-form'

    def clean(self):
        cleaned_data = super().clean()
        if 'school_props' in cleaned_data:
            cleaned_data['school_props'] = [s.split(' ') for s in cleaned_data['school_props']]
            print(cleaned_data)
        return cleaned_data
