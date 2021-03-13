import os
from django.conf import settings

FILE_ROOT = getattr(settings, "PAYMENT_FILE_ROOT",
                    os.path.join(settings.MEDIA_ROOT, "requisitions"))

options = {
    'page-size': 'A4',
    'cache-dir': os.path.join(FILE_ROOT, 'tmp/'),
    'enable-local-file-access': '',
    'margin-left': "30",
}

PDF_OPTIONS = getattr(settings, "PAYMENT_PDF_OPTIONS", options)
