from datetime import datetime
import uuid
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.shortcuts import render
from django.db import connection

def list_podcast(request):
    user_email = request.session.get('email')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.id, k.judul, k.tanggal_rilis, k.tahun, k.durasi, p.email_podcaster,
                   (SELECT COUNT(*) FROM episode e WHERE e.id_konten_podcast = p.id_konten) as episode_count
            FROM konten k
            INNER JOIN podcast p ON k.id = p.id_konten
        """)
        podcasts = cursor.fetchall()

    context = {
        'podcasts': podcasts,
        'user_email': user_email  
    }
    return render(request, 'podcast_list.html', context)


def podcast_detail(request, id):
    with connection.cursor() as cursor:
     
        cursor.execute("""
            SELECT k.id, k.judul, k.tanggal_rilis, k.tahun, k.durasi, p.email_podcaster,
                   (SELECT STRING_AGG(g.genre, ', ') 
                    FROM genre g 
                    WHERE g.id_konten = k.id) AS genres
            FROM konten k
            INNER JOIN podcast p ON k.id = p.id_konten
            WHERE k.id = %s
        """, [str(id)])
        podcast = cursor.fetchone()
        
        
        cursor.execute("""
            SELECT e.id_episode, e.judul, e.deskripsi, e.durasi, e.tanggal_rilis
            FROM episode e
            WHERE e.id_konten_podcast = %s
        """, [str(id)])
        episodes = cursor.fetchall()

    context = {
        'podcast': podcast,
        'episodes': episodes
    }
    return render(request, 'podcast_detail.html', context)

def add_podcast(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        duration = request.POST.get('duration')
        genres = request.POST.getlist('genres')
        email_podcaster = request.session.get('email') 
        
        if not email_podcaster:
            return HttpResponse("User is not authenticated")

        podcast_id = str(uuid.uuid4())  
        tanggal_rilis = datetime.now().date()
        tahun = datetime.now().year

        with connection.cursor() as cursor:
            
            cursor.execute("""
                INSERT INTO konten (id, judul, tanggal_rilis, tahun, durasi)
                VALUES (%s, %s, %s, %s, %s)
            """, [podcast_id, title, tanggal_rilis, tahun, duration])

            
            cursor.execute("""
                INSERT INTO podcast (id_konten, email_podcaster)
                VALUES (%s, %s)
            """, [podcast_id, email_podcaster])

            
            for genre in genres:
                cursor.execute("""
                    INSERT INTO genre (id_konten, genre)
                    VALUES (%s, %s)
                """, [podcast_id, genre])
        
        return redirect('kelola_podcast:list_podcast')

    return render(request, 'podcast_form.html')

def add_episode(request, id):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        duration = request.POST.get('duration')
        tanggal_rilis = datetime.now().date()

        episode_id = str(uuid.uuid4())  

        with connection.cursor() as cursor:
            # Insert into the episode table
            cursor.execute("""
                INSERT INTO episode (id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [episode_id, str(id), title, description, duration, tanggal_rilis])

        return redirect('kelola_podcast:podcast_detail', id=id)

    podcast_title = get_podcast_title(id) 
    context = {
        'podcast_id': id,
        'podcast_title': podcast_title
    }
    return render(request, 'episode_form.html', context)

def get_podcast_title(podcast_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT judul
            FROM konten
            WHERE id = %s
        """, [str(podcast_id)])
        row = cursor.fetchone()
    return row[0] if row else 'Podcast'