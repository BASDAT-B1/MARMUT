from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
import uuid
import random


# @login_required(login_url='/login')

# Create your views here.
def show_main(request):
    return render(request, "main.html")

def logout(request):
    try:
        del request.session['email']
    except KeyError:
        pass
    return redirect('main:login')

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
            # with connection.cursor() as cursor:
            #     cursor.execute("SELECT * FROM AKUN WHERE email = %s", [email])
            #     row = cursor.fetchone()
            request.session['email'] = user
            return redirect('main:dashboard_penggunabiasa')
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
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        gender = request.POST.get('gender')
        if gender == "Laki-laki":
            gender = 1
        else :
            gender = 0
        tempat_lahir = request.POST.get('tempatLahir')
        tanggal_lahir = request.POST.get('tanggalLahir')
        kota_asal = request.POST.get('kotaAsal')
        roles = request.POST.getlist('role')

        with connection.cursor() as cursor:
            cursor.execute("SELECT EMAIL FROM AKUN WHERE email = %s", [email])
            row = cursor.fetchone()
        if row != None :
            return HttpResponse("Email Already Registered")
        else :
            if len(roles) == 0:
                is_verified = False
            else: 
                is_verified = True
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO AKUN (email, password, nama, gender, tempat_lahir, tanggal_lahir, is_verified, kota_asal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, [email, password, nama, gender, tempat_lahir, tanggal_lahir, is_verified, kota_asal])
            if len(roles) > 0 :
                new_uuid = uuid.uuid4()
                uuid_pemilik_hak_cipta = uuid.uuid4()
                    
                rate_royalti = random.randint(1_000_000, 10_000000)
                pemilik_created = False
                for role in roles: 
                    role = role.upper()
                    if(role == "PODCASTER"):
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO PODCASTER (email)
                                VALUES (%s)
                            """, [email])
                    if(role == "ARTIST" or role == "SONGWRITER"):
                        if pemilik_created == False:
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO PEMILIK_HAK_CIPTA (id, rate_royalti)
                                    VALUES (%s, %s)
                                """, [uuid_pemilik_hak_cipta, rate_royalti])
                            pemilik_created = True
                        if(role == "ARTIST"):
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO ARTIST (id, email_akun, id_pemilik_hak_cipta)
                                    VALUES (%s, %s, %s)
                                """, [new_uuid, email, uuid_pemilik_hak_cipta])
                        else:
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO SONGWRITER (id, email_akun, id_pemilik_hak_cipta)
                                    VALUES (%s, %s, %s)
                                """, [new_uuid, email, uuid_pemilik_hak_cipta])

                    
                return redirect('main:login')
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
    if 'email' in request.session:
        user_email = request.session['email']
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM AKUN WHERE EMAIL = %s", [user_email])
            row = cursor.fetchone()
            print(row)
        gender = "Laki-laki" if row[3] else "Perempuan"
        context = {
            'nama' : row[2],
            'email' : row[0],
            'kota_asal' : row[7],
            'gender' : gender,
            'tempat_lahir': row[4],
            'tanggal_lahir': row[5],
        }
    return render(request, 'dashboard_penggunabiasa.html', context)

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
