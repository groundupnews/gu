
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.conf import settings as django_settings
from django.utils import timezone
from . import settings
from . import models
from newsroom.models import Author
from blocks.models import Group


def album_list(request):
    albums = models.Album.objects.all()
    return render(request, "gallery/album_list.html",
                  {'albums': albums, })


def album_detail(request, pk):
    album = get_object_or_404(models.Album, pk=pk)
    return render(request, "gallery/album_detail.html",
                  {'album': album, })


def photo_list(request, keyword=None):
    search_string = ""
    photographer = None
    featured = False
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
                       Q(keywords__name__icontains=search_string)
        query = query & search_query
        list_all = False

    if "photographer" in request.GET:
        list_all = False
        try:
            photographer_string = request.GET["photographer"]
            photographer = Author.objects.get(pk=int(photographer_string))
            query = query & Q(photographer=photographer)
        except:
            pass

    if "date" in request.GET:
        list_all = False
        try:
            date_string = request.GET["date"]
            date = timezone.datetime.strptime(date_string,"%Y%m%d")
            query = query & Q(date_taken=date)
        except:
            pass

    if "featured" in request.GET:
        list_all = False
        featured = True
        query = query & Q(featured=True)

    photos = models.Photograph.objects.filter(query).\
             ordered_by_date_taken().distinct()

    template= "gallery/photo_list.html"
    page_template='gallery/photo_list_page.html'

    if request.is_ajax():
        template = page_template

    return render(request, template,
                  {'photos': photos,
                   'page_template': page_template,
                   'keyword': keyword,
                   'search_string': search_string,
                   'photographer': photographer,
                   'featured': featured,
                   'list_all': list_all})


def photo_detail(request, pk):
    versions = {key: value for (key, value) in
                django_settings.FILEBROWSER_VERSIONS.items()
                if not key.startswith("admin")}

    versions = sorted(versions.items(),key=lambda x: x[1]["width"])
    try:
        blocks = Group.objects.get(name="Gallery_Front").get_blocks()
    except:
        blocks = []

    photo = get_object_or_404(models.Photograph, pk=pk)
    related_by_keyword = models.Photograph.objects.filter(keywords__in=
                                                   photo.keywords.all())
    related_by_album = models.Photograph.objects.filter(albums__in=
                                                 photo.albums.all())
    related_photos = (related_by_keyword | related_by_album).\
                     exclude(pk=photo.pk).distinct()

    template= "gallery/photo_detail.html"
    page_template='gallery/photo_list_page.html'

    if request.is_ajax():
        template = page_template

    return render(request, template,
                  {'blocks': blocks,
                   'page_template': page_template,
                   'photo':photo,
                   'default_copyright': settings.DEFAULT_COPYRIGHT,
                   'versions': versions,
                   'photos' : related_photos})


def gallery_front(request):
    try:
        blocks = Group.objects.get(name="Gallery_Front").get_blocks()
    except:
        blocks = []

    featured_photos = models.Photograph.objects.filter(featured=True).\
                         order_by('-modified')[:settings.NUM_FEATURED]
    photos = models.Photograph.objects.filter(featured=False).\
                    order_by('?')[:settings.NUM_LATEST]
    albums = models.Album.objects.all().order_by('?')\
                    [:settings.NUM_ALBUMS]
    return render(request, "gallery/index.html",
                  {'blocks' : blocks,
                   'featured_photos': featured_photos,
                   'photos': photos,
                   'albums': albums})
