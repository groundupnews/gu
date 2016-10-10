from django.conf import settings

DIRECTORY = getattr(settings, 'GALLERY_DIRECTORY', "images/Gallery")
