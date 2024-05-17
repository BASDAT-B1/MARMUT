from django.urls import path

from kelola_playlist.views import ( add_playlist, detail_playlist, playlist, add_playlist, delete_playlist, add_song_to_playlist, edit_playlist, delete_song_from_playlist, play_song, shuffle_play, play_playlist
)

app_name = 'kelola_playlist'

urlpatterns = [
    path('add_playlist/', add_playlist, name='add_playlist'),
    path('detail_playlist/<str:id_playlist>', detail_playlist, name='detail_playlist'),
    path('play_playlist/<str:id_playlist>', play_playlist, name='play_playlist'),
    path('playlist/', playlist, name='playlist'),
    path('delete_playlist/<str:id_playlist>/', delete_playlist, name='delete_playlist'),  
    path('add_song_to_playlist/<str:id_playlist>/', add_song_to_playlist, name='add_song_to_playlist'),
    path('edit_playlist/<str:id_playlist>/', edit_playlist, name='edit_playlist'),
    path('play_song/<str:id_song>/', play_song, name='play_song'),
    path('shuffle_play/<str:id_playlist>/', shuffle_play, name='shuffle_play'),
    path('delete_song_from_playlist/<str:id_playlist>/<str:id_song>/', delete_song_from_playlist, name='delete_song_from_playlist'),
]