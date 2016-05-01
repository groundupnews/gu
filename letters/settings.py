from django.conf import settings

EDITOR = getattr(settings, 'LETTERS_EDITOR', "")
DAYS_AGO = getattr(settings, 'LETTERS_DAYS_AGO', 14)
