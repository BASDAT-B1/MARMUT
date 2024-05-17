from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.db import connection
import uuid
import random
import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404



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
        roles = []
        
        user = authenticate(email, password)
        roles = []
        user_info = {}
        if user is not None:
            with connection.cursor() as cursor:
                cursor.execute("SELECT nama, kota_asal, gender, tempat_lahir, tanggal_lahir FROM AKUN WHERE email = %s", [email])
                user_info_row = cursor.fetchone()
                user_info = {
                    'nama': user_info_row[0],
                    'kota_asal': user_info_row[1],
                    'gender': 'Laki-laki' if user_info_row[2] == 1 else 'Perempuan',
                    'tempat_lahir': user_info_row[3],
                    'tanggal_lahir': user_info_row[4].strftime('%Y-%m-%d')  # Convert date to string
                }
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT EMAIL FROM PODCASTER WHERE email = %s", [email])
                row = cursor.fetchone()
                if row and row[0] == email:
                    roles.append('Podcaster')

            with connection.cursor() as cursor:
                cursor.execute("SELECT email_akun FROM ARTIST WHERE email_akun = %s", [email])
                row = cursor.fetchone()
                if row and row[0] == email:
                    roles.append('Artis')

            with connection.cursor() as cursor:
                cursor.execute("SELECT email_akun FROM SONGWRITER WHERE email_akun = %s", [email])
                row = cursor.fetchone()
                if row and row[0] == email:
                    print('masok')
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
            print(user_info)

            request.session['email'] = user
            request.session['roles'] = roles
            request.session['user_info'] = user_info

            return redirect('main:dashboard')
        else:
            return HttpResponse("Invalid credentials")

    return render(request, 'login.html')

def dashboard(request):
    email = request.session.get('email')
    roles = request.session.get('roles', [])
    podcasts = []
    songs = []
    albums = []
    playlists = []

    with connection.cursor() as cursor:
        if 'Podcaster' in roles:
            cursor.execute("""
                SELECT k.id, k.judul 
                FROM podcast p 
                JOIN konten k ON p.id_konten = k.id 
                WHERE p.email_podcaster = %s
            """, [email])
            podcasts = cursor.fetchall()

        if 'Artis' in roles or 'Songwriter' in roles:
            cursor.execute("""
                SELECT k.id, k.judul 
                FROM song s 
                JOIN konten k ON s.id_konten = k.id 
                WHERE s.id_artist = (SELECT id FROM artist WHERE email_akun = %s)
            """, [email])
            songs = cursor.fetchall()

        if 'Label' in roles:
            cursor.execute("""
                SELECT a.id, a.judul 
                FROM album a 
                WHERE a.id_label = (SELECT id FROM label WHERE email = %s)
            """, [email])
            albums = cursor.fetchall()

        cursor.execute("""
            SELECT up.id_user_playlist, up.judul 
            FROM user_playlist up 
            WHERE up.email_pembuat = %s
        """, [email])
        playlists = cursor.fetchall()

    context = {
        'podcasts': podcasts,
        'songs': songs,
        'albums': albums,
        'playlists': playlists,
    }

    return render(request, 'dashboard.html', context)


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
    search_query = request.GET.get('search', '')  # Get the search query from the GET request
    data = []
    
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
            data.append({
                'jenis': 'Song',
                'judul': song[0],
                'nama': song[1],
            })
        for podcast in podcasts_data:
            data.append({
                'jenis': 'Podcast',
                'judul': podcast[0],
                'nama': podcast[1],
            })
        for playlist in user_playlists_data:
            data.append({
                'jenis': 'User Playlist',
                'judul': playlist[0],
                'nama': playlist[1],
            })
    return render(request, 'search_page.html', {'data' : data,'search_query': search_query})

    

def langganan_paket(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PAKET;")
        row = cursor.fetchall()
    paket = []
    for paket_data in row:
        paket.append({
            'jenis': paket_data[0],
            'harga': paket_data[1]
        })

    if request.method == 'POST':
        print(request.POST)
        selected_jenis = request.POST['selected_jenis']
        selected_harga = request.POST['selected_harga']
        return redirect('main:pembayaran_paket', jenis=selected_jenis, harga=selected_harga)
    return render(request, 'langganan_paket.html', {'paket': paket})

def downloaded_songs(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ds.id_song, k.JUDUL, ak.NAMA
            FROM DOWNLOADED_SONG as ds, KONTEN as k, AKUN as ak, SONG as s, ARTIST as ar
            WHERE ds.id_song = k.id AND ds.id_song = s.id_konten AND s.id_artist = ar.id AND ar.email_akun = ak.email  AND ds.email_downloader = %s
        """, [request.session['email']])
        row = cursor.fetchall()
    data = []
    for song in row:
        data.append(
            {
            'id': song[0],
            'judul': song[1],
            'nama': song[2],
            }
        )
    return render(request, 'downloaded_songs.html', {'data': data})

@require_http_methods(["DELETE"])
def delete_song(request, song_id):
    if request.method == 'DELETE':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM DOWNLOADED_SONG WHERE id_song = %s", [song_id])
        return JsonResponse({'message': 'Song deleted successfully'}, status=200)
    return JsonResponse({'message': 'Failed to delete Song'})


def add_months(source_date, months):
    from calendar import monthrange
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    # Get the last day of the target month
    last_day_of_month = monthrange(year, month)[1]
    day = min(source_date.day, last_day_of_month)
    return datetime.date(year, month, day)


def pembayaran_paket(request, jenis, harga):
    context = {
        'jenis': jenis,
        'harga': harga
    }

    if request.method == 'POST':
        metode_pembayaran = request.POST['payment_method']
        user_email = request.session['email']
        new_id = uuid.uuid4()

        # Determine the duration in months based on the 'jenis'
        if jenis in ['1 Bulan', '3 Bulan', '6 Bulan']:
            date = int(jenis.split()[0])
        else:
            date = 12  # Default to 12 months for yearly subscription

        timestamp_dimulai = datetime.date.today()
        timestamp_berakhir = add_months(timestamp_dimulai, date)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TRANSACTION (ID, JENIS_PAKET, EMAIL, TIMESTAMP_DIMULAI, TIMESTAMP_BERAKHIR, METODE_BAYAR, NOMINAL)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [new_id, jenis, user_email, timestamp_dimulai, timestamp_berakhir, metode_pembayaran, int(harga)])

            cursor.execute("DELETE FROM NONPREMIUM WHERE email = %s", [user_email])
            cursor.execute("INSERT INTO PREMIUM (EMAIL) VALUES (%s)", [user_email])
            cursor.execute("UPDATE AKUN SET is_verified = true WHERE email = %s", [user_email])

        roles = request.session['roles']
        roles.remove("Pengguna Biasa")
        roles.append("Premium")
        request.session['roles'] = roles

    return render(request, 'pembayaran_paket.html', context)


def melihat_chart(request):
    return render(request,'melihat_chart.html')

def dashboard_label(request):
    return render(request, 'dashboard_label.html')

def dashboard_podcaster(request):
    email = request.session.get('email')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.id, k.judul 
            FROM podcast p
            JOIN konten k ON p.id_konten = k.id
            WHERE p.email_podcaster = %s
        """, [email])
        podcasts = cursor.fetchall()

    context = {
        'podcasts': podcasts,
        'user_info': request.session.get('user_info'),
        'roles': request.session.get('roles')
    }
    return render(request, 'dashboard_podcaster.html', context)

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
    user_email = request.session['email']
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM TRANSACTION WHERE email = %s", [user_email])
        row = cursor.fetchone()
    data = {
        'jenis' : row[1],
        'tanggal_mulai': row[3],
        'tanggal_akhir': row[4],
        'metode_pembayaran' : row[5],
        'nominal': row[6],
    }
    return render(request, 'riwayat_transaksi.html', data)

def dashboard_label_with_album(request):
    return render(request, 'dashboard_label_with_album.html')

def dashboard_podcaster_with_podcast(request):
    return render(request, 'dashboard_podcaster_with_podcast.html')

def dashboard_penggunabiasa_with_playlist(request):
    return render(request, 'dashboard_penggunabiasa_with_playlist.html')

def dashboard_artist_atau_songwriter_with_playlist(request):
    return render(request, 'dashboard_artist_atau_songwriter_with_playlist.html')