from django.shortcuts import redirect, render
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST


# Create your views here.
def song(request, id_song):
    roles = request.session['roles']
    with connection.cursor() as cursor:
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
    if "Pengguna Biasa" in roles :
        return render(request, 'song.html', context)

    else:
        return render(request, 'song_premium.html', context)

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

def download_song(request, id_song):
    email_downloader = request.session['email']

    with connection.cursor() as cursor:
        # Periksa apakah lagu sudah diunduh oleh pengguna
        cursor.execute("""
            SELECT COUNT(*)
            FROM DOWNLOADED_SONG
            WHERE id_song = %s AND email_downloader = %s
        """, [id_song, email_downloader])
        already_downloaded = cursor.fetchone()[0]

        if already_downloaded:
            # Jika sudah diunduh, tampilkan pesan
            cursor.execute("""
                SELECT k.judul
                FROM KONTEN k
                JOIN SONG s ON k.id = s.id_konten
                WHERE k.id = %s
            """, [id_song])
            song_title = cursor.fetchone()[0]

            context = {
                'message': f"Lagu dengan judul '{song_title}' sudah pernah di unduh!",
                'options': [
                    {'label': 'KE PLAYLIST', 'url': reverse('kelola_playlist:playlist')},
                    {'label': 'KEMBALI', 'url': reverse('play_song:song', args=[id_song])}
                ]
            }
            return render(request, 'message.html', context)

        else:
            # Jika belum diunduh, tambahkan entri ke tabel DOWNLOADED_SONG dan perbarui total_download
            waktu = timezone.now()
            cursor.execute("""
                INSERT INTO DOWNLOADED_SONG (id_song, email_downloader)
                VALUES (%s, %s)
            """, [id_song, email_downloader])

            cursor.execute("""
                UPDATE SONG
                SET total_download = total_download + 1
                WHERE id_konten = %s
            """, [id_song])

            cursor.execute("""
                SELECT k.judul
                FROM KONTEN k
                JOIN SONG s ON k.id = s.id_konten
                WHERE k.id = %s
            """, [id_song])
            song_title = cursor.fetchone()[0]

            context = {
                'message': f"Berhasil mengunduh Lagu dengan judul '{song_title}'!",
                'options': [
                    {'label': 'KE DAFTAR DOWNLOAD', 'url': reverse('main:downloaded_songs')},
                    {'label': 'KEMBALI', 'url': reverse('play_song:song', args=[id_song])}
                ]
            }
            return render(request, 'message.html', context)

def downloaded_songs(request):
    email_downloader = request.session['email']

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.judul, ak.nama, k.durasi, s.id_konten
            FROM DOWNLOADED_SONG ds
            JOIN SONG s ON ds.id_song = s.id_konten
            JOIN KONTEN k ON s.id_konten = k.id
            JOIN ARTIST ar ON s.id_artist = ar.id
            JOIN AKUN ak ON ak.email = ar.email_akun
            WHERE ds.email_downloader = %s
        """, [email_downloader])
        songs = cursor.fetchall()

    context = {
        'songs': [{'judul': song[0], 'artist': song[1], 'durasi': song[2], 'id_song': song[3]} for song in songs]
    }
    return render(request, 'downloaded_songs.html', context)