from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# @login_required(login_url='/login')

# Create your views here.
def show_main(request):
    return render(request, "main.html")

def login(request):
    context = {}
    return render (request, 'login.html', context)

def langganan_paket(request):
    return render(request, 'langganan_paket.html')

def downloaded_songs(request):
    return render(request, 'downloaded_songs.html')

def pembayaran_paket(request):
    return render(request, 'pembayaran_paket.html')

def melihat_chart(request):
    return render(request,'melihat_chart.html')