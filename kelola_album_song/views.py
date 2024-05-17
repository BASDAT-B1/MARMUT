from django.db import connection
from django.http import HttpResponse
from django.shortcuts import redirect, render
import uuid
from datetime import datetime

# Create your views here.

def list_album(request):
    label_email = request.session.get('email')
    if label_email:
        id_artist = None
        album_data = []

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT A.id
                FROM AKUN AK
                JOIN ARTIST A ON AK.email = A.email_akun
                WHERE AK.email = %s
            """, [label_email])
            result = cursor.fetchone()
            if result:
                id_artist = result[0]

            if id_artist:
                cursor.execute("""
                    SELECT DISTINCT A.id, A.judul, L.nama, A.jumlah_lagu, A.total_durasi
                    FROM ALBUM A
                    JOIN LABEL L ON A.id_label = L.id
                    JOIN SONG S ON A.id = S.id_album
                    WHERE S.id_artist = %s
                """, [id_artist])
                albums = cursor.fetchall()
                
                for album in albums:
                    album_data.append({
                        'id': album[0],
                        'judul': album[1],
                        'label': album[2],
                        'jumlah_lagu': album[3],
                        'total_durasi': album[4]
                    })
                
                print(album_data)

        return render(request, "list_album.html", {'albums': album_data})


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
                    result = cursor.fetchone()
                    if result:
                        id_label = result[0]
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                SELECT A.id, A.judul, A.jumlah_lagu, A.total_durasi
                                FROM ALBUM A
                                WHERE A.id_label = %s
                            """, [id_label])
                            albums = cursor.fetchall()
                        
                        album_data = []
                        for album in albums:
                            album_data.append({
                                'id' : album[0],
                                'judul': album[1],
                                'jumlah_lagu': album[2],
                                'total_durasi': album[3]
                        })
                        
                        return render(request, 'list_album_label.html', {'albums': album_data})
            

     

def create_album(request):
    roles = request.session.get('roles', [])
    print('tes')
    print(roles)
    if 'Artis' in roles or 'Songwriter' in roles:
        print('tes 1')
        if request.method == 'POST':
            label_email = request.session.get('email', None)

            if label_email:
                album = request.POST.get('Judul')
                label = request.POST.get("label")
                judul_lagu = request.POST.get("judul_lagu")
                artist = request.POST.get("Artist")
                songwriter = request.POST.getlist("songwriters")
                genre = request.POST.getlist("genre")
                durasi = request.POST.get("durasi")

                # Generate UUIDs for album and content
                id_album = uuid.uuid4()
                id_konten = uuid.uuid4()

             
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id FROM LABEL WHERE nama = %s
                    """, [label])
                    id_label = cursor.fetchone()[0]

              
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id FROM ARTIST WHERE nama = %s
                    """, [artist])
                    id_artist = cursor.fetchone()[0]

               
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO ALBUM (id, judul, jumlah_lagu, id_label, total_durasi)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [id_album, album, 1, id_label, durasi])

                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [id_konten, judul_lagu, current_datetime, current_datetime.split('-')[0], durasi])

                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO SONG (id_konten, id_artist, id_album, total_play, total_download)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [id_konten, id_artist, id_album, 0, 0])

             
                with connection.cursor() as cursor:
                    for g in genre:
                        cursor.execute("""
                            INSERT INTO GENRE (id_konten, genre)
                            VALUES (%s, %s)
                        """, [id_konten, g])

            
                with connection.cursor() as cursor:
                    for sw in songwriter:
                        cursor.execute("""
                            SELECT id FROM SONGWRITER WHERE nama = %s
                        """, [sw])
                        id_songwriter = cursor.fetchone()[0]
                        cursor.execute("""
                            INSERT INTO SONGWRITER_WRITE_SONG (id_songwriter, id_song)
                            VALUES (%s, %s)
                        """, [id_songwriter, id_konten])

                return render(request, "create_album_success.html")

        # If GET request, fetch necessary data
        else:
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT nama FROM LABEL")
                    nama_label = cursor.fetchall()

                with connection.cursor() as cursor:
                    cursor.execute("SELECT genre FROM GENRE")
                    data_genre = cursor.fetchall()

                aos_data = {
                    'artists': [],
                    'songwriters': [],
                    'labels': [label[0] for label in nama_label],
                    'user_role': roles,
                    'genres': [genre[0] for genre in data_genre]
                }

                if 'Artis' not in roles:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT nama FROM ARTIST")
                        artist_data = cursor.fetchall()
                        aos_data['artists'] = [artist[0] for artist in artist_data]
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                                       SELECT nama 
                                       FROM AKUN 
                                       WHERE email = %s""", [label_email])
                        nama_artist = cursor.fetchone()[0]
                        aos_data['artists'] = [nama_artist]

                if 'Songwriter' not in roles:
                    with connection.cursor() as cursor:
                        cursor.execute("""SELECT S.nama 
                                       FROM SONGWRITER S
                                       """)
                        songwriter_data = cursor.fetchall()
                        aos_data['songwriters'] = [songwriter[0] for songwriter in songwriter_data]
                        print( aos_data['songwriters'])
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT nama FROM AKUN WHERE email= %s", [label_email])
                        nama_songwriter = cursor.fetchone()[0]
                        aos_data['songwriters'] = [nama_songwriter]

                return render(request, "create_album.html", {'aos_data': aos_data})


def create_lagu_artist(request):
    roles = request.session.get('roles', [])
    if 'Artis' in roles:
        if request.method == 'POST':
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id FROM ARTIST WHERE email_akun = %s
                    """, [label_email])
                    id_artist = cursor.fetchone()[0]

                judul_lagu = request.POST.get("Judul")
                songwriters = request.POST.getlist("songwriters")
                genres = request.POST.getlist("genre")
                durasi = request.POST.get("durasi")
                id_album = request.GET.get('id', None)
                id_konten = uuid.uuid4()
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [id_konten, judul_lagu, formatted_datetime, current_datetime.year, durasi])

                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO SONG (id_konten, id_artist, id_album, total_play, total_download)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [id_konten, id_artist, id_album, 0, 0])

                with connection.cursor() as cursor:
                    for genre in genres:
                        cursor.execute("""
                            INSERT INTO GENRE (id_konten, genre)
                            VALUES (%s, %s)
                        """, [id_konten, genre])

                with connection.cursor() as cursor:
                    for songwriter in songwriters:
                        cursor.execute("""
                            SELECT S.id 
                            FROM SONGWRITER S 
                            JOIN AKUN A ON S.email_akun = A.email
                            WHERE nama = %s
                        """, [songwriter])
                        id_songwriter = cursor.fetchone()[0]
                        cursor.execute("""
                            INSERT INTO SONGWRITER_SONG (id_songwriter, id_song)
                            VALUES (%s, %s)
                        """, [id_songwriter, id_konten])

                return redirect('kelola_album_song:list_album')

        else:
            label_email = request.session.get('email', None)
            if label_email:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT nama FROM LABEL")
                    nama_label = cursor.fetchall()

                with connection.cursor() as cursor:
                    cursor.execute("SELECT genre FROM GENRE")
                    data_genre = cursor.fetchall()

                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT nama FROM AKUN WHERE email = %s
                    """, [label_email])
                    nama_artist = cursor.fetchone()[0]

                with connection.cursor() as cursor:
                    cursor.execute("""SELECT nama 
                                   FROM AKUN A
                                   JOIN SONGWRITER S ON A.email = S.email_akun """)
                    songwriter_data = cursor.fetchall()

                aos_data = {
                    'artists': [nama_artist],
                    'songwriters': [songwriter[0] for songwriter in songwriter_data],
                    'labels': [label[0] for label in nama_label],
                    'user_role': roles,
                    'genres': [genre[0] for genre in data_genre]
                }

                return render(request, "create_lagu_artist.html", {'aos_data': aos_data})

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
                    id_album = request.GET.get('id', None)
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

def daftar_lagu(request, id_album):
    with connection.cursor() as cursor:
        cursor.execute("SELECT judul FROM ALBUM WHERE id=%s", [id_album])
        judul_fetch = cursor.fetchone()
        judul_album = judul_fetch[0]

        cursor.execute("""
            SELECT K.id, K.judul, K.durasi, 
                    COALESCE(APS.total_play, 0) AS total_play, 
                    COALESCE(DS.total_download, 0) AS total_download
            FROM SONG S
            LEFT JOIN KONTEN K ON S.id_konten = K.id
            LEFT JOIN (
                SELECT id_song, COUNT(*) AS total_play 
                FROM akun_play_song 
                GROUP BY id_song
            ) AS APS ON S.id_konten = APS.id_song
            LEFT JOIN (
                SELECT id_song, COUNT(*) AS total_download 
                FROM downloaded_song 
                GROUP BY id_song
            ) AS DS ON S.id_konten = DS.id_song
            WHERE S.id_album = %s
        """, [id_album])
        songs = cursor.fetchall()

    song_data = []
    for song in songs:
        song_data.append({
            "id": song[0],
            'Judul': song[1],
            'Durasi': song[2],
            'Total Play': song[3],
            'Total Download': song[4]
        })

    return render(request, "daftar_lagu.html", {'songs': song_data, 'judul': judul_album, 'id': id_album})

def cek_royalti(request):
    roles = request.session.get('roles')
    label_email = request.session.get('email')
    royalti_data = []
    if 'Artis' in roles or 'Songwriter' in roles:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT
                k.judul AS judul_lagu,
                a.judul AS judul_album,
                s.total_play,
                s.total_download,
                r.jumlah
            FROM
                royalti r
            JOIN
                song s ON r.id_song = s.id_konten
            JOIN
                album a ON s.id_album = a.id
            JOIN
                konten k ON s.id_konten = k.id
            JOIN
                pemilik_hak_cipta phc ON r.id_pemilik_hak_cipta = phc.id
            WHERE
                phc.id IN (
                    SELECT DISTINCT phc.id
                    FROM
                        pemilik_hak_cipta phc
                    LEFT JOIN
                        artist ar ON ar.id_pemilik_hak_cipta = phc.id
                    LEFT JOIN
                        songwriter sw ON sw.id_pemilik_hak_cipta = phc.id
                    LEFT JOIN
                        akun a ON (ar.email_akun = a.email OR sw.email_akun = a.email)
                    WHERE
                        a.email = %s
                )
            """, [label_email])
            royaltis = cursor.fetchall()
            print(royaltis)
        for royalti in royaltis:
            royalti_data.append({
                'Judul_Lagu': royalti[0],
                'Judul_Album': royalti[1],
                'Total_Play': royalti[2],
                'Total_Download': royalti[3],
                'Total_Royalti_Didapat': royalti[4]
            })
            print(royalti)


    if "Label" in roles:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    konten.judul AS judul_lagu,
                    album.judul AS judul_album,
                    song.total_play,
                    song.total_download,
                    r.jumlah
                FROM song
                JOIN album ON song.id_album = album.id
                JOIN konten ON song.id_konten = konten.id
                JOIN label ON album.id_label = label.id
                JOIN pemilik_hak_cipta phc ON label.id_pemilik_hak_cipta = phc.id
                WHERE label.email = %s
            """,[label_email])
            royaltis = cursor.fetchall()
            print(royaltis)
        for royalti in royaltis:
            royalti_data.append({
                'Judul_Lagu': royalti[0],
                'Judul_Album': royalti[1],
                'Total_Play': royalti[2],
                'Total_Download': royalti[3],
                'Total_Royalti_Didapat': royalti[4]
            })
            print(royalti)
    

    return render(request, "cek_royalti.html", {'royalti': royalti_data})
    
def hapus_album(request):
    roles = request.session.get('roles', [])
    if 'Artis' in roles or 'Songwriter' in roles or 'Label' in roles:
         if request.method == 'POST':
            label_email = request.session.get('email', None)
            if label_email:
                id_album = request.GET.get('id', None)

                with connection.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM ALBUM WHERE id_album = %s;
                    """, [id_album])
                if 'Label' in roles:
                    return redirect("list_album_label")
                if 'Artis' in roles or 'Songwriter' in roles :
                      return redirect("list_album")
                     
def hapus_lagu(request):
    roles = request.session.get('roles', [])
    if 'Artis' in roles or 'Songwriter' in roles or 'Label' in roles:
          if request.method == 'POST':
            label_email = request.session.get('email', None)
            if label_email:
                id_song = request.GET.get('id', None)
                with connection.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM KONTEN WHERE judul = %s;
                    """, [id_song])
 
                return redirect("daftar_lagu")
                