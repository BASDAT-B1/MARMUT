from django.urls import path

from kelola_playlist.views import ( add_playlist, detail_playlist, playlist, no_playlist
)

app_name = 'kelola_playlist'

urlpatterns = [
    path('add_playlist/', add_playlist, name='add_playlist'),
    path('detail_playlist/<str:id_playlist>', detail_playlist, name='detail_playlist'),
    path('playlist/', playlist, name='playlist'),
    path('no_playlist/', no_playlist, name='no_playlist'),
]