from django.urls import path

from play_user_playlist.views import ( play_playlist
)

app_name = 'play_user_playlist'

urlpatterns = [
    path('play_playlist', play_playlist, name='play_playlist'),
]