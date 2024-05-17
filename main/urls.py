from django.urls import include, path

from main.views import *
app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('kelola_album_song', include('kelola_album_song.urls')),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('register_label/', register_label, name='register_label'),
    path('register_pengguna/', register_pengguna, name='register_pengguna'),
    path('langganan-paket/', langganan_paket, name='langganan_paket'),
    path('downloaded-songs/', downloaded_songs, name='downloaded_songs'),
    path('pembayaran-paket/<str:jenis>/<str:harga>', pembayaran_paket, name='pembayaran_paket'),
    path('melihat-chart/', melihat_chart, name='melihat_chart'),
    path('dashboard_artist_atau_songwriter/', dashboard_artist_atau_songwriter, name='dashboard_artist_atau_songwriter'),
    path('dashboard_label/', dashboard_label, name='dashboard_label'),
    path('dashboard_penggunabiasa/', dashboard_penggunabiasa, name='dashboard_penggunabiasa'),
    path('dashboard_podcaster/', dashboard_podcaster, name='dashboard_podcaster'),
    path('riwayat-transaksi/', riwayat_transaksi, name='riwayat_transaksi'),
    path('dashboard_label_with_album/', dashboard_label_with_album, name='dashboard_label_with_album'),
    path('dashboard_podcaster_with_podcast/', dashboard_podcaster_with_podcast, name='dashboard_podcaster_with_podcast'),
    path('dashboard_penggunabiasa_with_playlist/', dashboard_penggunabiasa_with_playlist, name='dashboard_penggunabiasa_with_playlist'),
    path('dashboard_artist_atau_songwriter_with_playlist/', dashboard_artist_atau_songwriter_with_playlist, name='dashboard_artist_atau_songwriter_with_playlist'),
    path('logout/', logout, name='logout'),
    path('search/', search_bar, name='search_bar'),
    path('dashboard/', dashboard, name='dashboard'),
    path('delete_song/<str:song_id>/', delete_song, name='delete_song'),
]