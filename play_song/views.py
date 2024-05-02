from django.shortcuts import render

# Create your views here.
def song_premium(request):
    return render(request, 'song_premium.html')

def song(request):
    return render(request, 'song.html')
