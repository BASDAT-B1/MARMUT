from django.shortcuts import render

# Create your views here.

def list_album(request):

    # kalau bikin backend bakal digabung terus di logic
    # if label atau songwriter/artist
    return render(request, "list_album.html")

def list_album_label(request):

    return render(request, "list_album_label.html")

def create_album(request):

    return render(request, "create_album.html")

def create_lagu_artist(request):
    # bakal di if terus dilogic untuk backend
    return render(request, "create_lagu_artist.html")

def create_lagu_songwriter(request):

    return render(request, "create_lagu_songwriter.html")

def daftar_lagu(request):

    return render(request, "daftar_lagu.html")

def cek_royalti(request):

    return render(request, "cek_royalti.html")

def hapus_album(request):

    return render(request,"list_album.html")

def hapus_lagu(request):

    return render(request, "daftar_lagu.html")

