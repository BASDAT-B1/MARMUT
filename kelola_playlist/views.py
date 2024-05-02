from django.shortcuts import render

# Create your views here.
def add_playlist(request):
    return render(request, 'add_playlist.html')

def detail_playlist(request):
    return render(request, 'detail_playlist.html')

def playlist(request):
    return render(request, 'playlist.html')

def no_playlist(request):
    return render(request, 'no_playlist.html')