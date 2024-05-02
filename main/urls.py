from django.urls import include, path
from main.views import show_main, login, langganan_paket, downloaded_songs, pembayaran_paket, melihat_chart

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('kelola_album_song', include('kelola_album_song.urls')),
    path('login/', login, name='login'),
    path('langganan-paket/', langganan_paket, name='langganan_paket'),
    path('downloaded-songs/', downloaded_songs, name='downloaded_songs'),
    path('pembayaran-paket/', pembayaran_paket, name='pembayaran_paket'),
    path('melihat-chart/', melihat_chart, name='melihat_chart'),
]