from django.db.models import Q
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
    search_string = ""
    list_all = True
    if keyword:
        query = Q(keywords__name__in=[keyword])
        list_all = False
    else:
        query = Q()

    if "search-photos" in request.GET:
        search_string = request.GET["search-photos"]
        search_query = Q(suggested_caption__icontains=search_string) | \
                       Q(photographer__last_name__icontains=search_string) | \
                       Q(photographer__first_names__icontains=search_string) | \
                       Q(keywords__name__in=[search_string])
        query = query & search_query
        list_all = False

    photos = models.Photograph.objects.filter(query).distinct()
    return render(request, "gallery/photo_list.html",
                  {'photos': photos,
                   'keyword': keyword,
                   'search_string': search_string,
                   'list_all': list_all})


def photo_detail(request, pk):
    photo = get_object_or_404(models.Photograph, pk=pk)
    return render(request, "gallery/photo_detail.html",
                  {'photo':photo,})
