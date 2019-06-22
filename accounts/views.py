from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if not username:
            return render(request, 'accounts/signup.html', {'error': 'Username must be provided'})
        if not password1 or not password2:
            return render(request, 'accounts/signup.html', {'error': 'Password must be provided'})
        if password1 != password2:
            return render(request, 'accounts/signup.html', {'error': 'Passwords are not equal'})
        try:
            User.objects.get(username=username)
            return render(request, 'accounts/signup.html', {'error': 'Username has already been taken'})
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
            return render(request, 'accounts/login.html', {'error': 'Username must be provided'})
        if not password:
            return render(request, 'accounts/login.html', {'error': 'Password must be provided'})
        user = auth.authenticate(request, username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html', {'error': 'Username login or password is incorrect'})
    else:
        return render(request, 'accounts/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')
