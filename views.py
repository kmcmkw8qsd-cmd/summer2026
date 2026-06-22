from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error = "Identifiants incorrects"
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='/')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='/')
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required(login_url='/')
def deen(request):
    return render(request, 'deen.html')

@login_required(login_url='/')
def sport(request):
    return render(request, 'sport.html')

@login_required(login_url='/')
def regime(request):
    return render(request, 'regime.html')

@login_required(login_url='/')
def learning(request):
    return render(request, 'learning.html')

@login_required(login_url='/')
def selfcare(request):
    return render(request, 'selfcare.html')

@login_required(login_url='/')
def homecare(request):
    return render(request, 'homecare.html')

def goals(request):
    return render(request, 'goals.html')