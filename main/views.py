from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection


# @login_required(login_url='/login')

# Create your views here.
def show_main(request):
    return render(request, "main.html")

def authenticate(email, password):
    # print(f"cek email {email}")
    # print(f"cek password {password}")
    with connection.cursor() as cursor:
        cursor.execute("SELECT password FROM AKUN WHERE email = %s", [email])
        row = cursor.fetchone()
        print(row)
    
    if row is None:
        print(f"No user found with email: {email}")
        return None  # User does not exist

    stored_password = row[0]
    # print(stored_password)
    if password == stored_password:
        # print("Password match!")
        return email  # Authentication successful
    else:
        # print("Password does not match")
        return None  # Authentication failed

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(email, password)
        if user is not None:
            print("success login broooooooooo")
            request.session['email'] = user
            return redirect('main:show_main')
        else:
            return HttpResponse("Invalid credentials")

    return render(request, 'login.html')

# def login(request):
#     return render (request, 'login.html')

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
