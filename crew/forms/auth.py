from .general import BSForm, ClassAnalysisForm
from django import forms
from django.core.urlresolvers import reverse
from django.forms import formset_factory
from crew.models import Subject
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, ButtonHolder, Fieldset, Field


class LoginForm(forms.Form):
    user_name_or_id = forms.CharField(max_length=20, label='姓名/工号')
    password = forms.CharField(widget=forms.PasswordInput, label='密码')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-4 col-sm-4'
        self.helper.field_class = 'col-md-8 col-sm-8'
        self.helper.form_action = reverse('crew:login')
        self.helper.form_method = 'POST'
        self.helper.form_tag = True
        self.helper.html5_required = True

        self.helper.layout = Layout(
            Field('user_name_or_id'),
            Field('password'),
            ButtonHolder(
                Submit('submit', '登录', css_class="btn btn-primary pull-right")
            )
        )
