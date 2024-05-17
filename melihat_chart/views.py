from django.db import connection
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
# Create your views here.
def show_weekly(request):
    now = datetime.now()
    print(now)
    last_week = now - timedelta(days=7)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.id, k.judul, k.tanggal_rilis, COUNT(aps.id_song) AS total_play, a.nama
            FROM akun_play_song aps
            JOIN song s ON aps.id_song = s.id_konten
            JOIN konten k ON s.id_konten = k.id
            JOIN artist ar ON s.id_artist = ar.id
            JOIN akun a ON ar.email_akun = a.email
            WHERE aps.waktu >= %s AND aps.waktu <= %s
            GROUP BY k.id, k.judul, k.tanggal_rilis, a.nama
            ORDER BY total_play DESC
            LIMIT 20
        """, [last_week, now])
        songs = cursor.fetchall()
    
    context = {
        'songs': songs
    }
    
    return render(request, "weekly20.html", context)

def show_daily(request):
    now = datetime.now()
    last_24_hours = now - timedelta(days=1)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.id, k.judul, k.tanggal_rilis, COUNT(aps.id_song) AS total_play, a.nama
            FROM akun_play_song aps
            JOIN song s ON aps.id_song = s.id_konten
            JOIN konten k ON s.id_konten = k.id
            JOIN artist ar ON s.id_artist = ar.id
            JOIN akun a ON ar.email_akun = a.email
            WHERE aps.waktu >= %s AND aps.waktu <= %s
            GROUP BY k.id, k.judul, k.tanggal_rilis, a.nama
            ORDER BY total_play DESC
            LIMIT 20
        """, [last_24_hours, now])
        songs = cursor.fetchall()
    
    context = {
        'songs': songs
    }
    
    return render(request, "daily20.html", context)