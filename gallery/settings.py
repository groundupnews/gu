from django.conf import settings

DIRECTORY = getattr(settings, 'GALLERY_DIRECTORY', "images/Gallery")
FEATURED = getattr(settings, 'GALLERY_FEATURED', 5)
