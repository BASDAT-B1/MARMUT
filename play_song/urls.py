from django.urls import path

from play_song.views import ( song, update_song_progress, download_song,downloaded_songs, add_song_to_user_playlist, add_song_to_user_playlist_form
)

app_name = 'play_song'

urlpatterns = [
    path('song/<str:id_song>', song, name='song'),
    path('update_song_progress/<str:id_song>', update_song_progress, name='update_song_progress'),
    path('download_song/<str:id_song>/', download_song, name='download_song'),
    path('downloaded_songs/', downloaded_songs, name='downloaded_songs'),
    path('add_song_to_user_playlist_form/<str:id_song>/', add_song_to_user_playlist_form, name='add_song_to_user_playlist_form'),
    path('add_song_to_user_playlist/', add_song_to_user_playlist, name='add_song_to_user_playlist'),
]