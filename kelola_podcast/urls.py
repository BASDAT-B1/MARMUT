from django.urls import path
from .views import add_episode, add_podcast, list_podcast, podcast_detail

app_name = 'kelola_podcast'

urlpatterns = [
    path('', list_podcast, name='list_podcast'),
    path('podcast/id/', podcast_detail, name='podcast_detail'),
    path('add/', add_podcast, name='add_podcast'),
    path('episode/add/', add_episode, name='add_episode'),
]
