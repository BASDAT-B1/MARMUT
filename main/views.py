from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login')

# Create your views here.
def show_main(request):

    return render(request, "main.html")