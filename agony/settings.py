from django.conf import settings

AGONY_EMAIL = getattr(settings, 'AGONY_EMAIL', "")
AGONY_EMAIL_RECIPIENTS  = getattr(settings, 'AGONY_EMAIL_RECIPIENTS', [])
