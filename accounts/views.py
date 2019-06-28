from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if not username:
            return render(request, 'accounts/signup.html', {'error': _('username_empty_error')})
        if not password1 or not password2:
            return render(request, 'accounts/signup.html', {'error': _('password_empty_error')})
        if password1 != password2:
            return render(request, 'accounts/signup.html', {'error': _('passwords_not_equal_error')})
        try:
            User.objects.get(username=username)
            return render(request, 'accounts/signup.html', {'error': _('username_exists_error')})
        except User.DoesNotExist:
            user = User.objects.create_user(username, password=password1)
            auth.login(request, user)
            return redirect('home')
    else:
        return render(request, 'accounts/signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not username:
            return render(request, 'accounts/login.html', {'error': _('username_empty_error')})
        if not password:
            return render(request, 'accounts/login.html', {'error': _('password_empty_error')})
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'error': _('login_or_password_error')})
    else:
        return render(request, 'accounts/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')
