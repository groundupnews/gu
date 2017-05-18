from django.conf import settings

DIRECTORY = getattr(settings, 'GALLERY_DIRECTORY', "images")
NUM_FEATURED = getattr(settings, 'GALLERY_NUM_FEATURED', 5)
NUM_LATEST = getattr(settings, 'GALLERY_NUM_LATEST', 8)
NUM_ALBUMS = getattr(settings, 'GALLERY_NUM_ALBUMS', 4)
DEFAULT_COPYRIGHT = getattr(settings, 'GALLERY_DEFAULT_COPYRIGHT',
'<p>© 2016 GroundUp. <a href="http://creativecommons.org/licenses/by-nd/4.0/" rel="license"><img alt="Creative Commons License" src="https://i.creativecommons.org/l/by-nd/4.0/80x15.png" style="border-width:0"></a><br>This image is licensed under a <a href="http://creativecommons.org/licenses/by-nd/4.0/" rel="license">Creative Commons Attribution-NoDerivatives 4.0 International License</a>.</p>')
