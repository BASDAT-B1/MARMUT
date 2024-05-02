from django.shortcuts import render

# Create your views here.

def play_playlist(request):
    return render(request, 'play_playlist.html')
