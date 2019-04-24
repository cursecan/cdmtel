from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

from .forms import LoginForm


def loginView(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        print(form.errors)
        print(form.confirm_login_allowed())
        if form.is_valid():
            print(form.cleaned_data)

    content = {
        'form': form
    }
    return render(request, 'registration/login.html', content)