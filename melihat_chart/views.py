from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.

def show_weekly(request):
    return render(request, "weekly20.html")

def show_daily(request):
    return render(request, "daily20.html")