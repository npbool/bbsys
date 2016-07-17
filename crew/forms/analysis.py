from .general import BSForm, ClassAnalysisForm
from django import forms
from django.forms import formset_factory
from crew.models import Subject


class LevelRankForm(BSForm):
    use_rank = forms.ChoiceField(choices=((True, "排名"), (False, "分数")), initial=True, label="划线依据")
    level_a_rank = forms.IntegerField(label="一本排名", min_value=1)
    level_b_rank = forms.IntegerField(label="二本排名", min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(False, *args, **kwargs)


class LevelSubjectScoreForm(forms.Form):
    level_a_score = forms.FloatField(label="一本分数")
    level_b_score = forms.FloatField(label="二本分数")
    subject_name = forms.CharField(max_length=10, widget=forms.TextInput, disabled=True, )
    subject_pk = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level_a_score'].widget.attrs = {'class': 'form-control'}
        self.fields['level_b_score'].widget.attrs = {'class': 'form-control'}
        self.fields['subject_name'].widget.attrs = {'class': 'form-control'}

LevelSubjectScoreFormSet = formset_factory(LevelSubjectScoreForm)


class AnalysisLevelForm(ClassAnalysisForm):
    show_subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), label="统计单科", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(False, *args, **kwargs)
