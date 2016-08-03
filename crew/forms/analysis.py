from django import forms
from django.forms import formset_factory
from crew.models import Subject
from crispy_forms.helper import FormHelper, Layout
from crew.models import *


class ClassAnalysisForm(forms.Form):
    semester = forms.ModelChoiceField(label="学期", queryset=Semester.objects.all())
    exam = forms.ModelChoiceField(label="考试", queryset=Exam.objects.all())
    grade = forms.TypedChoiceField(label="年级", choices=Choices.GRADE_CHOICES, coerce=lambda x: int(x))
    category = forms.ChoiceField(label="文理", choices=Student.CATEGORY_CHOICES, initial='U')
    school_props = forms.MultipleChoiceField(
        choices=(
            (school[0] + ' ' + prop[0], school[1] + prop[1]) for school in Choices.SCHOOL_CHOICES for prop in
            Student.PROP_CHOICES
        ),
        initial=(
            [school[0] + ' ' + prop[0] for school in Choices.SCHOOL_CHOICES for prop in Student.PROP_CHOICES]
        ),
        label="类型",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 col-sm-4'
        self.helper.field_class = 'col-md-9 col-sm-8'
        self.helper.html5_required = True
        self.helper.form_tag = False
        self.fields['semester'].initial = Semester.objects.first()
        self.fields['exam'].initial = SystemSettings.get_instance().default_exam

    def clean(self):
        cleaned_data = super().clean()
        if 'school_props' in cleaned_data:
            cleaned_data['school_props'] = [s.split(' ') for s in cleaned_data['school_props']]
        return cleaned_data


class LevelRankForm(forms.Form):
    use_rank = forms.TypedChoiceField(choices=((1, "排名"), (0, "分数")), coerce=lambda x: int(x) == 1, initial=True,
                                      label="划线依据")
    level_a_rank = forms.IntegerField(label="一本排名", min_value=1)
    level_b_rank = forms.IntegerField(label="二本排名", min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = 'id-student-form'
        self.helper.form_class = 'form'
        self.helper.html5_required = True


class LevelSubjectScoreForm(forms.Form):
    level_a_score = forms.FloatField(label="一本分数")
    level_b_score = forms.FloatField(label="二本分数")
    subject_name = forms.CharField(max_length=10)
    subject_pk = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level_a_score'].widget.attrs = {'class': 'form-control'}
        self.fields['level_b_score'].widget.attrs = {'class': 'form-control'}
        self.fields['subject_name'].widget.attrs = {'class': 'form-control', 'readonly': 'readonly'}
        self.helper = FormHelper()
        self.helper.form_tag = False


LevelSubjectScoreFormSet = formset_factory(LevelSubjectScoreForm, extra=0)


class AnalysisLevelForm(ClassAnalysisForm):
    show_subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), label="统计单科", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnalysisLevelDistForm(AnalysisLevelForm):
    # show_subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), label="统计单科", required=False)
    class_idx = forms.IntegerField(min_value=1, label="班级")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'semester', 'exam', 'grade', 'class_idx', 'category', 'school_props', 'show_subjects'
        )


class AnalysisSegForm(ClassAnalysisForm):
    show_total = forms.BooleanField(label="统计总分", initial=True, required=False)
    show_subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), label="统计单科", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if (not cleaned_data.get('show_total', False)) and (not cleaned_data.get('show_subjects', [])):
            self.add_error('show_subjects', '总分和单科至少选一项')
        return cleaned_data


class AnalysisAvgForm(ClassAnalysisForm):
    show_subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), label="统计单科", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnalysisAvgCmpForm(AnalysisAvgForm):
    semester_cmp = forms.ModelChoiceField(label="比较学期", queryset=Semester.objects.all())
    exam_cmp = forms.ModelChoiceField(label="比较考试", queryset=Exam.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
