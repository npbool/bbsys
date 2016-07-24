from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from crew.forms.auth import *
from crew.models import Staff


@require_http_methods(['GET', 'POST'])
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_name_or_id = form.cleaned_data['user_name_or_id']
            password = form.cleaned_data['password']
            try:
                if str.isnumeric(user_name_or_id):
                    user = Staff.objects.get(staff_id=int(user_name_or_id)).user
                else:
                    user = User.objects.get(username=user_name_or_id)
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect(reverse("crew:student_query"))
                else:
                    form.add_error('password', '密码错误')
            except Staff.DoesNotExist:
                form.add_error('user_name_or_id', '找不到用户')
            except User.DoesNotExist:
                form.add_error('user_name_or_id', '找不到用户')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('crew:login'))
