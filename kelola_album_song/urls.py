from django.urls import path

from kelola_album_song.views import (
    cek_royalti, create_album, create_lagu_artist, daftar_lagu,
    hapus_album, hapus_lagu, list_album, list_album_label
)

app_name = 'kelola_album_song'

urlpatterns = [
    # path('', show_main, name='show_main'),
    path('list_album/', list_album, name='list_album'),
    path('list_album_label/', list_album_label, name='list_album_label'),
    path('create_album/', create_album, name='create_album'),
    path('create_lagu_artist/<str:id_album>', create_lagu_artist, name='create_lagu_artist'),
    path('daftar_lagu/<str:id_album>', daftar_lagu, name='daftar_lagu'),
    path('cek_royalti/', cek_royalti, name='cek_royalti'),
    path('hapus_album/<str:id_album>', hapus_album, name='hapus_album'),
    path('hapus_lagu/<str:id_song>', hapus_lagu, name='hapus_lagu')
]
