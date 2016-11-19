from django.conf import settings

DIRECTORY = getattr(settings, 'GALLERY_DIRECTORY', "images/Gallery")
NUM_FEATURED = getattr(settings, 'GALLERY_NUM_FEATURED', 5)
NUM_LATEST = getattr(settings, 'GALLERY_NUM_LATEST', 7)
NUM_ALBUMS = getattr(settings, 'GALLERY_NUM_ALBUMS', 4)
