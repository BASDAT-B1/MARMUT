import uuid
from django.shortcuts import redirect, render
from django.db import IntegrityError, connection
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

# Create your views here.
def detail_playlist(request, id_playlist):
    if request.method == 'GET':
        if 'email' in request.session:
            user_email = request.session['email']
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT up.judul, a.nama, up.jumlah_lagu, up.total_durasi, up.tanggal_dibuat, up.deskripsi
                FROM USER_PLAYLIST up
                JOIN AKUN a ON up.email_pembuat = a.email
                WHERE up.id_user_playlist = %s AND a.email = %s
            """, [id_playlist, user_email])
            playlist_detail = cursor.fetchone()

        if not playlist_detail:
            return redirect('kelola_playlist:playlist')  
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT k.judul, ak.nama, k.durasi, k.id, ps.id_playlist
                FROM PLAYLIST_SONG ps
                JOIN KONTEN k ON ps.id_song = k.id
                JOIN SONG s ON k.id = s.id_konten
                JOIN ARTIST ar ON s.id_artist = ar.id
                JOIN AKUN ak ON ak.email = ar.email_akun
                WHERE ps.id_playlist = %s
            """, [id_playlist])
            songs = cursor.fetchall()
            print(songs)
        song_data = []
        for song in songs:
            song_data.append({
                'judul': song[0],
                'artist': song[1],
                'durasi': song[2],
                'id_song': song[3]
            })

        return render(request, 'detail_playlist.html', {
            'playlist_detail': playlist_detail,
            'songs': song_data,
            'id_playlist': id_playlist
        })

def play_playlist(request, id_playlist):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT up.judul, a.nama, up.jumlah_lagu, up.total_durasi, up.tanggal_dibuat, up.deskripsi
                FROM USER_PLAYLIST up
                JOIN AKUN a ON up.email_pembuat = a.email
                WHERE up.id_user_playlist = %s 
            """, [id_playlist])
            playlist_detail = cursor.fetchone()

        if not playlist_detail:
            return redirect('kelola_playlist:playlist')  
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT k.judul, ak.nama, k.durasi, k.id
                FROM PLAYLIST_SONG ps
                JOIN KONTEN k ON ps.id_song = k.id
                JOIN SONG s ON k.id = s.id_konten
                JOIN ARTIST ar ON s.id_artist = ar.id
                JOIN AKUN ak ON ak.email = ar.email_akun
                WHERE ps.id_playlist = %s
            """, [id_playlist])
            songs = cursor.fetchall()

        song_data = []
        for song in songs:
            song_data.append({
                'judul': song[0],
                'artist': song[1],
                'durasi': song[2],
                'id_song': song[3]
            })

        return render(request, 'play_playlist.html', {
            'playlist_detail': playlist_detail,
            'songs': song_data,
            'id_playlist': id_playlist
        })
    
def playlist(request):
    if request.method == 'GET':
        if 'email' in request.session:
            user_email = request.session['email']
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT up.id_playlist, up.judul, up.jumlah_lagu, up.total_durasi
                FROM USER_PLAYLIST up
                JOIN AKUN a ON up.email_pembuat = a.email
                WHERE a.email = %s
            """, [user_email])
            playlists = cursor.fetchall()
        
        playlist_data = []
        for playlist in playlists:
            playlist_data.append({
                'id': playlist[0],
                'judul': playlist[1],
                'jumlah_lagu': playlist[2],
                'total_durasi': playlist[3]
            })
        
        return render(request, 'playlist.html', {'playlists': playlist_data})

def delete_playlist(request, id_playlist):
    if request.method == 'POST':
        if 'email' in request.session:
            user_email = request.session['email']
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM USER_PLAYLIST
                WHERE id_user_playlist = %s AND email_pembuat = %s
            """, [id_playlist, user_email])
        
        return redirect('kelola_playlist:playlist')
    
def add_playlist(request):
    if request.method == 'POST':
        judul = request.POST['judul']
        deskripsi = request.POST['deskripsi']
        user_email = request.session.get('email')

        if not user_email:
            return redirect('login.html')

        id_playlist = str(uuid.uuid4())

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO PLAYLIST (id)
                VALUES (%s)
            """, [id_playlist])

            cursor.execute("""
                INSERT INTO USER_PLAYLIST (id_user_playlist, judul, deskripsi, email_pembuat, jumlah_lagu, total_durasi, tanggal_dibuat, id_playlist)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
            """, [id_playlist, judul, deskripsi, user_email, 0, 0, id_playlist])
        
        return redirect('kelola_playlist:playlist')
    return render(request, 'add_playlist.html')

def edit_playlist(request, id_playlist):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT up.judul, up.deskripsi
                FROM USER_PLAYLIST up
                WHERE up.id_user_playlist = %s
            """, [id_playlist])
            playlist = cursor.fetchone()

        if not playlist:
            return redirect('kelola_playlist:playlist') 

        return render(request, 'edit_playlist.html', {
            'id_playlist': id_playlist,
            'judul': playlist[0],
            'deskripsi': playlist[1],
        })

    elif request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')

        if not judul or not deskripsi:
            return render(request, 'edit_playlist.html', {
                'id_playlist': id_playlist,
                'judul': judul,
                'deskripsi': deskripsi,
                'error': 'Judul and Deskripsi are required'
            })

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE USER_PLAYLIST
                SET judul = %s, deskripsi = %s
                WHERE id_user_playlist = %s
            """, [judul, deskripsi, id_playlist])

        return redirect(reverse('kelola_playlist:detail_playlist', args=[id_playlist]))
    
def get_songs():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.judul, ak.nama, k.id
            FROM KONTEN k
            JOIN SONG s ON k.id = s.id_konten
            JOIN ARTIST ar ON s.id_artist = ar.id
            JOIN AKUN ak ON ak.email = ar.email_akun
        """)
        songs = cursor.fetchall()
    return [
        {'judul': song[0], 'artist': song[1], 'id': song[2]}
        for song in songs
    ]

def add_song_to_playlist(request, id_playlist):
    if request.method == 'GET':
        print(f"GET request received for playlist ID: {id_playlist}")
        songs = get_songs()
        return render(request, 'add_song.html', {
            'id_playlist': id_playlist,
            'songs': songs
        })

    elif request.method == 'POST':
        print(f"POST request received for playlist ID: {id_playlist}")
        song_id = request.POST.get('song_id')
        print(f"Song ID from POST request: {song_id}")

        if not song_id:
            print("Song ID is required but not provided.")
            songs = get_songs()
            return render(request, 'add_song.html', {
                'id_playlist': id_playlist,
                'songs': songs,
                'error': 'Song ID is required'
            })

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id
                FROM PLAYLIST, USER_PLAYLIST
                WHERE id_user_playlist = %s AND id_playlist = id
            """, [id_playlist])
            playlist_exists = cursor.fetchone()[0]
            print(f"Playlist exists: {playlist_exists}")

            if not playlist_exists:
                print(f"Playlist with ID {id_playlist} does not exist.")
                songs = get_songs()
                return render(request, 'add_song.html', {
                    'id_playlist': id_playlist,
                    'songs': songs,
                    'error': 'Playlist does not exist'
                })

            cursor.execute("""
                SELECT COUNT(*)
                FROM PLAYLIST_SONG
                WHERE id_playlist = %s AND id_song = %s
            """, [id_playlist, song_id])
            count = cursor.fetchone()[0]
            print(f"Song already in playlist: {count > 0}")

            if count > 0:
                print(f"Song with ID {song_id} is already in the playlist.")
                songs = get_songs()
                return render(request, 'add_song.html', {
                    'id_playlist': id_playlist,
                    'songs': songs,
                    'error': 'Lagu sudah ada di playlist'
                })

            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO PLAYLIST_SONG (id_playlist, id_song)
                        VALUES (%s, %s)
                    """, [playlist_exists, song_id])
                print(f"Lagu dengan id {song_id} berhasil ditambahkan ke playlist {playlist_exists}")
            except IntegrityError as e:
                print(f"IntegrityError: {e}")
                songs = get_songs()
                return render(request, 'add_song.html', {
                    'id_playlist': id_playlist,
                    'songs': songs,
                    'error': 'Failed to add song to playlist. Please try again.'
                })

            return redirect(reverse('kelola_playlist:detail_playlist', args=[id_playlist]))
        
def delete_song_from_playlist(request, id_playlist, id_song):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM PLAYLIST_SONG
                WHERE id_playlist = %s AND id_song = %s
            """, [id_playlist, id_song])

        return redirect(reverse('kelola_playlist:detail_playlist', args=[id_playlist]))
    else:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT k.judul, ak.nama
                FROM PLAYLIST_SONG ps
                JOIN KONTEN k ON ps.id_song = k.id
                JOIN SONG s ON k.id = s.id_konten
                JOIN ARTIST ar ON s.id_artist = ar.id
                JOIN AKUN ak ON ak.email = ar.email_akun
                WHERE ps.id_playlist = %s AND ps.id_song = %s
            """, [id_playlist, id_song])
            song = cursor.fetchone()

        if not song:
            return redirect(reverse('kelola_playlist:detail_playlist', args=[id_playlist]))

        return render(request, 'confirm_delete_song.html', {
            'id_playlist': id_playlist,
            'id_song': id_song,
            'song_title': song[0],
            'artist_name': song[1]
        })

def play_song(request, id_song):
    email_pemain = request.session['email']
    waktu = timezone.now()

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu)
            VALUES (%s, %s, %s)
        """, [email_pemain, id_song, waktu])

        cursor.execute("""
            UPDATE SONG
            SET total_play = total_play + 1
            WHERE id_konten = %s
        """, [id_song])

    return redirect(reverse('kelola_playlist:detail_playlist', args=[id_song]))

def shuffle_play(request, id_playlist):
    email_pemain = request.session['email']
    waktu = timezone.now()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT email_pembuat
            FROM USER_PLAYLIST
            WHERE id_playlist = %s
        """, [id_playlist])
        email_pembuat = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO AKUN_PLAY_USER_PLAYLIST (email_pemain, id_user_playlist, email_pembuat, waktu)
            VALUES (%s, %s, %s, %s)
        """, [email_pemain, id_playlist, email_pembuat, waktu])

        cursor.execute("""
            SELECT id_song
            FROM PLAYLIST_SONG
            WHERE id_playlist = %s
        """, [id_playlist])
        songs = cursor.fetchall()

        for song in songs:
            cursor.execute("""
                INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu)
                VALUES (%s, %s, %s)
            """, [email_pemain, song[0], waktu])

    return redirect(reverse('kelola_playlist:detail_playlist', args=[id_playlist]))