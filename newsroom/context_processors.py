from django.conf import settings
from newsroom import settings as newsroom_settings
import random

def newsroom_template_variables(request):
    return {'logo': newsroom_settings.LOGO,
            'ACME_ADS': settings.ACME_ADS,
            'GOOGLE_ADS': settings.GOOGLE_ADS,
            'AMAZON_ADS': settings.AMAZON_ADS,
            'AB_TEST_ADS': settings.AB_TEST_ADS,
            'AD_OPTIONS': random.randint(0, 1)}
