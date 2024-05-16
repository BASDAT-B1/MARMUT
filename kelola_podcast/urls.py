from django.urls import path
from .views import add_episode, add_podcast, list_podcast, podcast_detail, delete_podcast

app_name = 'kelola_podcast'

urlpatterns = [
    path('', list_podcast, name='list_podcast'),
    path('podcast/<uuid:id>/', podcast_detail, name='podcast_detail'),
    path('add/', add_podcast, name='add_podcast'),
     path('episode/<uuid:id>/add', add_episode, name='add_episode'),
     path('podcast/<uuid:id>/delete', delete_podcast, name='delete_podcast')
]
