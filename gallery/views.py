from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.conf import settings as django_settings
from django.core.paginator import Paginator
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

    if "q" in request.GET:
        search_string = request.GET["q"]
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

    items_per_page = 16
    paginator = Paginator(photos, items_per_page)
    page_number = request.GET.get('page')
    
    if page_number == 'last':
        page_number = paginator.num_pages
        
    page_obj = paginator.get_page(page_number)

    return render(request, "gallery/photo_list.html", {
        'page_obj': page_obj,
        'keyword': keyword,
        'search_string': search_string,
        'photographer': photographer,
        'featured': featured,
        'list_all': list_all
    })


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

    items_per_page = 16
    paginator = Paginator(related_photos, items_per_page)
    page_number = request.GET.get('page')
    
    if page_number == 'last':
        page_number = paginator.num_pages
        
    page_obj = paginator.get_page(page_number)

    return render(request, "gallery/photo_detail.html", {
        'blocks': blocks,
        'page_obj': page_obj,
        'photo':photo,
        'default_copyright': settings.DEFAULT_COPYRIGHT,
        'versions': versions,
        'photos_count' : related_photos.count()
    })


def gallery_front(request):
    try:
        blocks = Group.objects.get(name="Gallery_Front").get_blocks()
    except:
        blocks = []

    featured_photos = models.Photograph.objects.filter(featured=True).\
                         order_by('-modified')[:settings.NUM_FEATURED]
    photos = models.Photograph.objects.filter(featured=False)[:settings.NUM_LATEST]
    albums = models.Album.objects.all()[:settings.NUM_ALBUMS]
    return render(request, "gallery/index.html",
                  {'blocks' : blocks,
                   'featured_photos': featured_photos,
                   'photos': photos,
                   'albums': albums})
