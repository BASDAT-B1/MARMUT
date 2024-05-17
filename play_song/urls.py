from django.urls import path

from play_song.views import ( song, song_premium, update_song_progress
)

app_name = 'play_song'

urlpatterns = [
    path('song/<str:id_song>', song, name='song'),
    path('song_premium/', song_premium, name='song_premium'),
    path('update_song_progress/<str:id_song>', update_song_progress, name='update_song_progress'),
]