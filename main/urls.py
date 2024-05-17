from django.urls import include, path
from main.views import *

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
    path('riwayat-transaksi/', riwayat_transaksi, name='riwayat_transaksi'),
    path('logout/', logout, name='logout'),
    path('search/', search_bar, name='search_bar'),
    path('dashboard/', dashboard, name='dashboard'),
    path('delete_song/<str:song_id>/', delete_song, name='delete_song'),
]