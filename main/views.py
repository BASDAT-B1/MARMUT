from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.db import connection
import uuid
import random



# Create your views here.
def show_main(request):
    return render(request, "main.html")

def logout(request):
    try:
        del request.session['email']
        del request.session['roles']
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
        roles = []
        if user is not None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT EMAIL FROM PODCASTER WHERE email = %s", [email])
                row = cursor.fetchone()
                if row and row[0] == email:
                    roles.append('Podcaster')

            with connection.cursor() as cursor:
                cursor.execute("SELECT email_akun FROM ARTIST WHERE email_akun = %s", [email])
                row = cursor.fetchone()
                print(row)
                if row and row[0] == email:
                    roles.append('Artis')

            with connection.cursor() as cursor:
                cursor.execute("SELECT email_akun FROM SONGWRITER WHERE email_akun = %s", [email])
                row = cursor.fetchone()
                if row and row[0] == email:
                    roles.append('Songwriter')

            with connection.cursor() as cursor:
                cursor.execute("SELECT EMAIL FROM LABEL WHERE email = %s", [email])
                row = cursor.fetchone()
                if row and row[0] == email:
                    roles.append('Label')

            with connection.cursor() as cursor:
                cursor.execute("SELECT EMAIL FROM PREMIUM WHERE email = %s", [email])
                row = cursor.fetchone()
                if row and row[0] == email:
                    roles.append('Premium')
                else:
                    roles.append('Pengguna Biasa')

            request.session['email'] = user
            request.session['roles'] = roles

            return redirect('main:dashboard_penggunabiasa')
        else:
            return HttpResponse("Invalid credentials")

    return render(request, 'login.html')

def register(request):
    return render (request, 'register.html')

def register_label(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        kontak = request.POST.get('kontak')
        uuid_label = uuid.uuid4()

        with connection.cursor() as cursor:
            cursor.execute("SELECT EMAIL FROM LABEL WHERE EMAIL = %s", email)
            row = cursor.fetchone()

        if row == email:
            return HttpResponse("Email Already Exist")

        rate_royalti = random.randint(1_000_000, 100_000_000)
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO PEMILIK_HAK_CIPTA (id, rate_royalti)
                VALUES (%s, %s)
            """, [uuid_label, rate_royalti])

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO LABEL (id, nama, email, kontak, id_pemilik_hak_cipta, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [uuid_label, nama, email, kontak, uuid_label, password])
        return redirect('main:login')

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
                    
                rate_royalti = random.randint(1_000_000, 100_000_000)
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
                                """, [new_uuid, rate_royalti])
                            pemilik_created = True
                        if(role == "ARTIST"):
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO ARTIST (id, email_akun, id_pemilik_hak_cipta)
                                    VALUES (%s, %s, %s)
                                """, [new_uuid, email, new_uuid])
                        else:
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO SONGWRITER (id, email_akun, id_pemilik_hak_cipta)
                                    VALUES (%s, %s, %s)
                                """, [new_uuid, email, new_uuid])
                return redirect('main:login')
    return render (request, 'register_pengguna.html')

def search_bar(request):
    search_query = request.GET.get('search')  # Get the search query from the GET request
    user_playlists = []
    podcasts = []
    songs = []
    
    if search_query != '':  # Only execute the query if there is a search term
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT up.JUDUL, ak.NAMA
                FROM USER_PLAYLIST as up, AKUN as ak
                WHERE judul ILIKE %s AND up.EMAIL_PEMBUAT = ak.EMAIL;
            """, [f'%{search_query}%'])
            user_playlists_data = cursor.fetchall()

            cursor.execute("""
                SELECT k.JUDUL, ak.NAMA
                FROM PODCAST as p, AKUN as ak, KONTEN as k
                WHERE judul ILIKE %s AND p.EMAIL_PODCASTER = ak.EMAIL AND p.id_konten = k.id;
            """, [f'%{search_query}%'])
            podcasts_data = cursor.fetchall()

            cursor.execute("""
                SELECT k.JUDUL, ak.NAMA
                FROM SONG as s, AKUN as ak, KONTEN as k, ARTIST as ar
                WHERE judul ILIKE %s AND s.id_konten = k.id AND ar.email_akun = ak.email AND s.id_artist = ar.id;
            """, [f'%{search_query}%'])
            songs_data = cursor.fetchall()
        for song in songs_data:
            songs.append({
                'judul': song[0],
                'nama': song[1],
            })
        for podcast in podcasts_data:
            podcasts.append({
                'judul': podcast[0],
                'nama': podcast[1],
            })
        for playlist in user_playlists_data:
            user_playlists.append({
                'judul': playlist[0],
                'nama': playlist[1],
            })
    return render(request, 'search_page.html', {'user_playlists': user_playlists, 'podcasts': podcasts, 'songs': songs,'search_query': search_query})

    

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
        roles = request.session['roles']
        print(roles)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM AKUN WHERE EMAIL = %s", [user_email])
            row = cursor.fetchone()
        gender = "Laki-laki" if row[3] else "Perempuan"
        context = {
            'nama' : row[2],
            'email' : row[0],
            'kota_asal' : row[7],
            'gender' : gender,
            'tempat_lahir': row[4],
            'tanggal_lahir': row[5],
            'roles': roles
        }
    return render(request, 'dashboard_penggunabiasa.html', context)

def dashboard_artist_atau_songwriter(request):
    return render(request, 'dashboard_artist_atau_songwriter.html')

def dashboard_label_with_album(request):
    return render(request, 'dashboard_label_with_album.html')

def dashboard_podcaster_with_podcast(request):
    return render(request, 'dashboard_podcaster_with_podcast.html')

def dashboard_penggunabiasa_with_playlist(request):
    return render(request, 'dashboard_penggunabiasa_with_playlist.html')

def dashboard_artist_atau_songwriter_with_playlist(request):
    return render(request, 'dashboard_artist_atau_songwriter_with_playlist.html')
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
