from django.urls import path

from play_song.views import ( song, song_premium
)

app_name = 'play_song'

urlpatterns = [
    path('song/', song, name='song'),
    path('song_premium/', song_premium, name='song_premium'),
]