from django.conf import settings
from newsroom import settings as newsroom_settings


def newsroom_template_variables(request):
    return {'logo': newsroom_settings.LOGO,
            'ACME_ADS': settings.ACME_ADS,
            'GOOGLE_ADS': settings.GOOGLE_ADS}
