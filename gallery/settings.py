from django.conf import settings

GALLERY_FOLDER = getattr(settings, 'NEWSROOM_ARTICLE_COPYRIGHT', "images/Gallery/")
