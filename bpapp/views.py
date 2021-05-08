# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.sessions.models import Session  

user = {}
displayImportData = False
def index(request):
    if request.method == 'POST' and not user and request.POST["login"] == "admin":
        user["login"] = request.POST['login']
        context = {
            'login' : user["login"]
        }
        messages.success(request, "User Logged in Successfully")
        return render(request, 'main.html', context=context)
    elif user:
        context = {
            'login' : user["login"]
        }
        return render(request, 'main.html', context=context)
    elif not user:
        return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')

def logout(request):
    if user:
        user.clear()
        return redirect('/')
    else:
        return render(request, 'index.html')

def data(request):
    displayImportData = True
    if user:
        context = {
            'displayImportData' : displayImportData,
            'login' : user["login"]
        }
    return render(request, 'main.html', context=context)