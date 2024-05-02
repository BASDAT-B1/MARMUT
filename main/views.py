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

def register(request):
    return render (request, 'register.html')

def register_label(request):
    return render (request, 'register_label.html')

def register_pengguna(request):
    return render (request, 'register_pengguna.html')

def langganan_paket(request):
    return render(request, 'langganan_paket.html')

def downloaded_songs(request):
    return render(request, 'downloaded_songs.html')

def pembayaran_paket(request):
    return render(request, 'pembayaran_paket.html')

def melihat_chart(request):
    return render(request,'melihat_chart.html')

def dashboard_label(request):
    return render(request, 'dashboard_label.html')

def dashboard_podcaster(request):
    return render(request, 'dashboard_podcaster.html')

def dashboard_penggunabiasa(request):
    return render(request, 'dashboard_penggunabiasa.html')

def dashboard_artist_atau_songwriter(request):
    return render(request, 'dashboard_artist_atau_songwriter.html')

def riwayat_transaksi(request):
    return render(request, 'riwayat_transaksi.html')

def dashboard_label_with_album(request):
    return render(request, 'dashboard_label_with_album.html')

def dashboard_podcaster_with_podcast(request):
    return render(request, 'dashboard_podcaster_with_podcast.html')

def dashboard_penggunabiasa_with_playlist(request):
    return render(request, 'dashboard_penggunabiasa_with_playlist.html')

def dashboard_artist_atau_songwriter_with_playlist(request):
    return render(request, 'dashboard_artist_atau_songwriter_with_playlist.html')
