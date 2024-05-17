from django.shortcuts import redirect, render
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST


# Create your views here.
def song_premium(request):
    return render(request, 'song_premium.html')

def song(request, id_song):
    with connection.cursor() as cursor:
        # Fetch song details
        cursor.execute("""
            SELECT k.judul, k.durasi, k.tanggal_rilis, k.tahun, s.total_play, s.total_download, a.judul
            FROM SONG s
            JOIN KONTEN k ON s.id_konten = k.id
            JOIN ALBUM a ON s.id_album = a.id
            WHERE k.id = %s
        """, [id_song])
        song_detail = cursor.fetchone()

        # Fetch genres
        cursor.execute("""
            SELECT g.genre
            FROM GENRE g
            WHERE g.id_konten = %s
        """, [id_song])
        genres = cursor.fetchall()

        # Fetch artist
        cursor.execute("""
            SELECT ak.nama
            FROM ARTIST ar
            JOIN SONG s ON ar.id = s.id_artist
            JOIN ARTIST ON s.id_artist = ar.id
            JOIN AKUN ak ON ak.email = ar.email_akun
            WHERE s.id_konten = %s
        """, [id_song])
        artist = cursor.fetchone()

        # Fetch songwriters
        cursor.execute("""
            SELECT ak.nama
            FROM SONGWRITER sw
            JOIN SONGWRITER_WRITE_SONG sws ON sw.id = sws.id_songwriter
            JOIN AKUN ak ON ak.email = sw.email_akun
            WHERE sws.id_song = %s
        """, [id_song])
        songwriters = cursor.fetchall()

    context = {
        'id_song': id_song,
        'judul': song_detail[0],
        'durasi': song_detail[1],
        'tanggal_rilis': song_detail[2],
        'tahun': song_detail[3],
        'total_play': song_detail[4],
        'total_downloads': song_detail[5],
        'album': song_detail[6],
        'genres': [genre[0] for genre in genres],
        'artist': artist[0] if artist else 'Unknown',
        'songwriters': [songwriter[0] for songwriter in songwriters]
    }

    return render(request, 'song.html', context)

@require_POST
def update_song_progress(request, id_song):
    progress = int(request.POST.get('progress', 0))
    if progress > 70:
        email_pemain = request.session['email']
        waktu = timezone.now()

        with connection.cursor() as cursor:
            # Tambahkan entri ke tabel AKUN_PLAY_SONG
            cursor.execute("""
                INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu)
                VALUES (%s, %s, %s)
            """, [email_pemain, id_song, waktu])

            # Perbarui total_play di tabel SONG
            cursor.execute("""
                UPDATE SONG
                SET total_play = total_play + 1
                WHERE id_konten = %s
            """, [id_song])

    return redirect(reverse('play_song:song', args=[id_song]))