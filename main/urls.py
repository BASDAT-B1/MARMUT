from django.urls import include, path
from main.views import show_main

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('kelola_album_song', include('kelola_album_song.urls')),
]