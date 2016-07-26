from .general import BSForm, ClassAnalysisForm
from django import forms
from django.forms import formset_factory
from crew.models import Subject
from crispy_forms.helper import FormHelper, Layout


class LevelRankForm(BSForm):
    use_rank = forms.TypedChoiceField(choices=((1, "排名"), (0, "分数")), coerce=lambda x: int(x) == 1, initial=True,
                                      label="划线依据")
    level_a_rank = forms.IntegerField(label="一本排名", min_value=1)
    level_b_rank = forms.IntegerField(label="二本排名", min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(False, *args, **kwargs)
        self.helper.form_tag = False


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
        super().__init__(False, *args, **kwargs)


class AnalysisLevelDistForm(AnalysisLevelForm):
    # show_subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), label="统计单科", required=False)
    class_idx = forms.IntegerField(min_value=1, label="班级")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            'semester', 'exam', 'grade', 'class_idx', 'category', 'school_props', 'show_subjects'
        )

