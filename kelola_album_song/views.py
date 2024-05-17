from django.db import connection
from django.shortcuts import render
import uuid
from datetime import datetime

# Create your views here.

def list_album(request):
    roles = request.session.get('roles', [])
    if 'Artist' in roles or 'Songwriter' in roles or 'Label' in roles:
        if request.method == 'GET':
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT A.judul, L.nama, A.jumlah_lagu, A.total_durasi
                        FROM ALBUM A
                    """,)
                    albums = cursor.fetchall()
                
                album_data = []
                for album in albums:
                    album_data.append({
                        'judul': album[0],
                        'label': album[1],
                        'jumlah_lagu': album[2],
                        'total_durasi': album[3]
                    })

                return render(request, "list_album.html",{'albums': album_data})

def list_album_label(request):
    roles = request.session.get('roles', [])
    if 'Label' in roles :
        if request.method == 'GET':
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id FROM LABEL WHERE email = %s
                    """, [label_email])
                    id_label = cursor.fetchone()[0]

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT A.judul, A.jumlah_lagu, A.total_durasi
                    FROM ALBUM A
                    WHERE A.id_label = %s
                """, [id_label])
                albums = cursor.fetchall()
            
            album_data = []
            for album in albums:
                album_data.append({
                    'judul': album[0],
                    'jumlah_lagu': album[1],
                    'total_durasi': album[2]
            })
            
            return render(request, 'list_album_label.html', {'albums': album_data})
        

     

def create_album(request):
    roles = request.session.get('roles', [])
    if 'Artist' in roles or 'Songwriter' in roles :
        if request.method == 'POST':
            label_email = request.session.get('email', None)

            if label_email:
                album = request.POST.get('Judul')
                label = request.POST.get("label")
                judul_lagu = request.POST.get("judul_lagu")
                artist = request.POST.get("artist")
                songwriter = request.POST.get("songwriter")

                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id FROM LABEL
                    """)
                    nama_label = cursor.fetchall()

                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT genre FROM GENRE
                    """)
                    data_genre = cursor.fetchall()
                aos_data = []
                if 'Artist' not in roles :
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT A.nama
                            FROM  ARTIST A
                        """)
                        artist_data = cursor.fetchall()
                        aos_data.append(artist_data)
                else :
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT nama FROM ARTIST WHERE email_akun = %s
                        """, [label_email])
                        nama_artist = cursor.fetchone()[0]
                        aos_data.append(nama_artist)

                if 'Songwriter' not in roles :
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT S.nama
                            FROM SONGWRITER S 
                        """)
                        songwriter_data = cursor.fetchall()
                        aos_data.append(songwriter_data)
                else :
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT nama FROM SONGWRITER WHERE email_akun = %s
                        """, [label_email])
                        nama_songwriter = cursor.fetchone()[0]
                        aos_data.append(nama_songwriter)

                aos_data.append(nama_label)
                aos_data.append(roles)
                aos_data.append(genre)
                aos_data_fix = []
                for aos in aos_data:
                    aos_data_fix.append({
                    'artists': aos[0],
                    'songwriters': aos[1],
                    'labels':aos[2],
                    'user_role': aos[3],
                    'genre': aos[4],
                })
                    
                genre = request.POST.getlist("genre")
                durasi = request.POST.get("durasi")
                id_album = uuid.uuid4()

                id_konten = uuid.uuid4()
                with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT L.id 
                            FROM LABEL L
                            WHERE L.nama = %s    
                        """, [label])
                id_label = cursor.fetchone()[0]

                with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT A.id 
                            FROM  ARTIST A
                            WHERE A.nama = %s    
                        """, [artist])
                id_artist = cursor.fetchone()[0]

                with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO ALBUM (id, judul, jumlah_lagu, id_label, total_durasi)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [id_album, album, 1, id_label , durasi])

                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

                with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [judul_lagu,formatted_datetime, 2024, durasi])     
            
                with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO SONG (id_artist, id_album, total_play, total_download)
                            VALUES (%s, %s, %s, %s)
                            WHERE id_konten = %s
                        """, [id_artist, id_album, 0 , 0, id_konten])     

                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO GENRE (id_konten, genre)
                        VALUES (%s, %s)
                    """, [id_konten, genre])     
                return render(request, "create_album.html",{'artist_or_songwriter': aos_data_fix})
            


def create_lagu_artist(request):
    roles = request.session.get('roles', [])
    if 'Artist' in roles :
        if request.method == 'POST':
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, FROM ARTIST WHERE email = %s
                    """, [label_email])
                    id_artist = cursor.fetchone()[0]

                judul_lagu = request.POST.get("judul_lagu")
                songwriter = request.POST.get("songwriter")
                genre = request.POST.get("genre")
                durasi = request.POST.get("durasi")
                id_album = request.POST.get("id_album")
                id_konten = uuid.uuid4()
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
                with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [judul_lagu,formatted_datetime, 2024, durasi])

                with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO SONG (id_konten, id_artist, id_album, total_play, total_download)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [id_konten, id_artist, id_album, 0 , 0])

                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO GENRE (id_konten, genre)
                        VALUES (%s, %s)
                    """, [id_konten, genre])     
                return render(request, "create_lagu_artist.html")

def create_lagu_songwriter(request):
    roles = request.session.get('roles', [])
    if 'Songwriter' in roles :
        if request.method == 'POST':
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, FROM SONGWRITER WHERE email = %s
                    """, [label_email])
                    id_songwriter = cursor.fetchone()[0]
                    judul_lagu = request.POST.get("judul_lagu")
                    artist = request.POST.get("artist")
                    genre = request.POST.get("genre")
                    durasi = request.POST.get("durasi")
                    id_album = request.POST.get("id_album")
                    with connection.cursor() as cursor:
                            cursor.execute("""
                                SELECT A.id 
                                FROM  ARTIST A
                                WHERE A.nama = %s    
                            """, [artist])
                    id_artist = cursor.fetchone()[0]
                    id_konten = uuid.uuid4()

                    current_datetime = datetime.now()
                    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi)
                                VALUES (%s, %s, %s, %s, %s)
                            """, [judul_lagu,formatted_datetime, 2024, durasi])

                    with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO SONG (id_konten, id_artist, id_album, total_play, total_download)
                                VALUES (%s, %s, %s, %d, %d)
                            """, [id_konten, id_artist, id_album, 0 , 0])
                    
                    with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO GENRE (id_konten, genre)
                                VALUES (%s, %s)
                            """, [id_konten, genre])     
                    return render(request, "create_lagu_songwriter.html")

def daftar_lagu(request):
    roles = request.session.get('roles', [])
    if 'Artist' in roles or 'Songwriter' in roles or 'Label' in roles:
        if request.method == 'GET':
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                     cursor.execute("""
                    SELECT K.judul, K.durasi, S.total_play, S.total_download
                    FROM SONG S
                    LEFT JOIN KONTEN K ON S.id_konten = K.id
                """)
                songs = cursor.fetchall()

                song_data = []
                for song in songs:
                    song_data.append({
                        'Judul': song[0],
                        'Durasi': song[1],
                        'Total Play': song[2],
                        'Total Download': song[3]
                })

                return render(request, "daftar_lagu.html",{'songs': song_data})

def cek_royalti(request):
    roles = request.session.get('roles', [])
    if 'Artist' in roles or 'Songwriter' in roles or 'Label' in roles:
        if request.method == 'GET':
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                    cursor.execute("""
                            SELECT 
                            K.judul AS "Judul Lagu", 
                            A.judul AS "Judul Album", 
                            S.total_play AS "Total Play", 
                            S.total_download AS "Total Download",
                            S.total_play * PH.rate_royalti AS "Total Royalti Didapat"
                            FROM SONG S
                            LEFT JOIN KONTEN K ON S.id_konten = K.id
                            LEFT JOIN ALBUM A ON S.id_album = A.id
                            LEFT JOIN ROYALTI R ON R.id_song = S.id_konten
                            LEFT JOIN PEMILIK_HAK_CIPTA PH ON R.id_pemilik_hak_cipta = PH.id;          
                """,)
                royaltis = cursor.fetchall()
                royalti_data = []
                for royalti in royaltis:
                    royalti_data.append({
                        'Judul Lagu': royalti[0],
                        'Judul Album': royalti[1],
                        'Total Play': royalti[2],
                        'Total Download': royalti[3],
                        'Total Royalti Didapat': royalti[4]
                    })

                return render(request, "cek_royalti.html",{'royalti': royalti_data} )

def hapus_album(request):

    # album = request.POST.get('Judul')
    # with connection.cursor() as cursor:
    #     cursor.execute("""
    #         SELECT A.id
    #         FROM ALBUM A
    #         WHERE A.judul = %s;
    #     """, [album])
    # id_album = cursor.fetchone()[0]

    # with connection.cursor() as cursor:
    #     cursor.execute("""
    #         DELETE FROM ALBUM WHERE id_konten = %s;
    #     """, [id_album])
    return render(request,"list_album.html")

def hapus_lagu(request):
    # id_konten = request.POST.get("id_konten")

    # with connection.cursor() as cursor:
    #     cursor.execute("""
    #         DELETE FROM SONG WHERE id_konten = %s;
    #     """, [id_konten])

    return render(request, "daftar_lagu.html")