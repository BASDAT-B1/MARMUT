from django.shortcuts import render
from django.db import connection

# Create your views here.
def add_playlist(request):
    return render(request, 'add_playlist.html')

def detail_playlist(request):
    return render(request, 'detail_playlist.html')

def playlist(request):
    if(request.method == 'GET'):
        if 'email' in request.session:
            user_email = request.session['email']
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT up.id_user_playlist, up.judul, up.jumlah_lagu, up.total_durasi
                FROM USER_PLAYLIST up
                JOIN AKUN a ON up.email_pembuat = a.email
                WHERE a.email = %s
            """, [user_email])
    return render(request, 'playlist.html')

def no_playlist(request):
    return render(request, 'no_playlist.html')