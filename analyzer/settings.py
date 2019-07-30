from django.conf import settings

LOG_FILE = getattr(settings, "ANALYZER_LOG_FILE", "")
