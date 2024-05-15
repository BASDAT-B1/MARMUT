from django.shortcuts import render
from django.db import connection

# Create your views here.
def add_playlist(request):
    return render(request, 'add_playlist.html')

def detail_playlist(request, playlist_id):
    if request.method == 'GET':
        if 'email' in request.session:
            user_email = request.session['email']
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT up.judul, a.nama, up.jumlah_lagu, up.total_durasi, up.tanggal_dibuat, up.deskripsi
                FROM USER_PLAYLIST up
                JOIN AKUN a ON up.email_pembuat = a.email
                WHERE up.id_user_playlist = %s AND a.email = %s
            """, [playlist_id, user_email])
            playlist_detail = cursor.fetchone()
        
        cursor.execute("""
            SELECT s.judul, ar.nama, s.durasi
            FROM PLAYLIST_SONG ps
            JOIN SONG s ON ps.id_song = s.id_konten
            JOIN ARTIST ar ON s.id_artist = ar.id
            WHERE ps.id_playlist = %s
        """, [playlist_id])
        songs = cursor.fetchall()
        
        song_data = []
        for song in songs:
            song_data.append({
                'judul': song[0],
                'artist': song[1],
                'durasi': song[2]
            })
        
        return render(request, 'playlist_detail.html', {
            'playlist_detail': playlist_detail,
            'songs': song_data
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

def no_playlist(request):
    return render(request, 'no_playlist.html')