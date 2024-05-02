from django.urls import include, path

from main.views import show_main, login, langganan_paket, downloaded_songs, pembayaran_paket, melihat_chart, dashboard_artist_atau_songwriter, dashboard_label, dashboard_penggunabiasa, dashboard_podcaster, show_main, login, langganan_paket, downloaded_songs, pembayaran_paket, register,register_label,register_pengguna, riwayat_transaksi

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
    path('pembayaran-paket/', pembayaran_paket, name='pembayaran_paket'),
    path('melihat-chart/', melihat_chart, name='melihat_chart'),
    path('dashboard_artist_atau_songwriter/', dashboard_artist_atau_songwriter, name='dashboard_artist_atau_songwriter'),
    path('dashboard_label/', dashboard_label, name='dashboard_label'),
    path('dashboard_penggunabiasa/', dashboard_penggunabiasa, name='dashboard_penggunabiasa'),
    path('dashboard_podcaster/', dashboard_podcaster, name='dashboard_podcaster'),
    path('riwayat-transaksi/', riwayat_transaksi, name='riwayat_transaksi'),
]