from django.shortcuts import render

# Create your views here.

def list_podcast(request):
    return render(request, 'podcast_list.html')

def podcast_detail(request):
    return render(request, 'podcast_detail.html')

def add_podcast(request):
    return render(request, 'podcast_form.html')

def add_episode(request):
    return render(request, 'episode_form.html')
