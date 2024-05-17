from django.urls import path

from play_song.views import ( song, song_premium, update_song_progress, download_song,downloaded_songs
)

app_name = 'play_song'

urlpatterns = [
    path('song/<str:id_song>', song, name='song'),
    path('song_premium/<str:id_song>', song_premium, name='song_premium'),
    path('update_song_progress/<str:id_song>', update_song_progress, name='update_song_progress'),
    path('download_song/<str:id_song>/', download_song, name='download_song'),
    path('downloaded_songs/', downloaded_songs, name='downloaded_songs'),
]