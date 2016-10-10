from django.shortcuts import render
from django.shortcuts import get_object_or_404, render

from . import models

def album_list(request):
    albums = models.Album.objects.all()
    return render(request, "gallery/album_list.html",
                  {'albums':albums,})


def album_detail(request, pk):
    album = get_object_or_404(models.Album, pk=pk)
    return render(request, "gallery/album_detail.html",
                  {'album':album,})


def photo_list(request, keyword=None):
    if keyword is None:
        photos = models.Photograph.objects.all()
    else:
        photos = models.Photograph.objects.filter(keywords__name__in=[keyword])
    return render(request, "gallery/photo_list.html",
                  {'photos':photos,
                   'keyword': keyword})


def photo_detail(request, pk):
    photo = get_object_or_404(models.Photograph, pk=pk)
    return render(request, "gallery/photo_detail.html",
                  {'photo':photo,})
