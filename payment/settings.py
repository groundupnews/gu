import os
from django.conf import settings

FILE_ROOT = getattr(settings, "PAYMENT_FILE_ROOT",
                    os.path.join(settings.MEDIA_ROOT, "requisitions"))
