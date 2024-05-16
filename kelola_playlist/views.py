import uuid
from django.shortcuts import redirect, render
from django.db import connection
from django.http import HttpResponseForbidden
from django.urls import reverse

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
            return redirect('kelola_playlist:playlist')  # Redirect if playlist not found
        
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

        return render(request, 'detail_playlist.html', {
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
                SELECT up.id_user_playlist, up.judul, up.jumlah_lagu, up.total_durasi
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

        id_user_playlist = str(uuid.uuid4())
        id_playlist = str(uuid.uuid4())

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO PLAYLIST (id)
                VALUES (%s)
            """, [id_playlist])

            cursor.execute("""
                INSERT INTO USER_PLAYLIST (id_user_playlist, judul, deskripsi, email_pembuat, jumlah_lagu, total_durasi, tanggal_dibuat, id_playlist)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
            """, [id_user_playlist, judul, deskripsi, user_email, 0, 0, id_playlist])
        
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
            return redirect('kelola_playlist:playlist')  # Redirect if playlist not found

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
    
def add_song_to_playlist(request, id_playlist):
    with connection.cursor() as cursor:
            cursor.execute("""
                SELECT k.judul, ak.nama, k.id
                FROM KONTEN k
                JOIN SONG s ON k.id = s.id_konten
                JOIN ARTIST ar ON s.id_artist = ar.id
                JOIN AKUN ak ON ak.email = ar.email_akun
            """)
            songs = cursor.fetchall()
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT k.judul, ak.nama, k.id
                FROM KONTEN k
                JOIN SONG s ON k.id = s.id_konten
                JOIN ARTIST ar ON s.id_artist = ar.id
                JOIN AKUN ak ON ak.email = ar.email_akun
            """)
            songs = cursor.fetchall()
            
        song_options = [
            {'judul': song[0], 'artist': song[1], 'id': song[2]}
        for song in songs]

        return render(request, 'add_song.html', {
            'id_playlist': id_playlist,
            'songs': song_options
        })
    elif request.method == 'POST':
        print("POST data:", request.POST)
        song_id = request.POST.get('song_id')
        
        if not song_id:
            return render(request, 'add_song.html', {
                'id_playlist': id_playlist,
                'error': 'Song ID is required'
            })

        with connection.cursor() as cursor:
            # Check if song is already in playlist
            cursor.execute("""
                SELECT COUNT(*)
                FROM PLAYLIST_SONG
                WHERE id_playlist = %s AND id_song = %s
            """, [id_playlist, song_id])
            count = cursor.fetchone()[0]

            if count > 0:
                return render(request, 'add_song.html', {
                    'id_playlist': id_playlist,
                    'error': 'Lagu sudah ada di playlist'
                })

            # Add song to playlist
            cursor.execute("""
                INSERT INTO PLAYLIST_SONG (id_playlist, id_song)
                VALUES (%s, %s)
            """, [id_playlist, song_id])

            return redirect(reverse('kelola_playlist:detail_playlist', args=[id_playlist]))
        
def delete_song_from_playlist(request, id_playlist, id_song):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # Delete the song from the playlist
            cursor.execute("""
                DELETE FROM PLAYLIST_SONG
                WHERE id_playlist = %s AND id_song = %s
            """, [id_playlist, id_song])

        return redirect(reverse('kelola_playlist:detail_playlist', args=[id_playlist]))
    else:
        # Fetch the song details to confirm deletion
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