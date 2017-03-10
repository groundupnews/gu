from django.conf import settings


ARTICLE_COPYRIGHT = getattr(settings, 'NEWSROOM_ARTICLE_COPYRIGHT', "")
ARTICLES_PER_PAGE = getattr(settings, 'NEWSROOM_ARTICLES_PER_PAGE', 16)
BEAUTIFUL_SOUP_PARSER = getattr(settings, 'NEWSROOM_BEAUTIFUL_SOUP_PARSER',
                                "lxml")
ARTICLE_SUMMARY_IMAGE_SIZE = getattr(settings,
                                     'NEWSROOM_ARTICLE_TEASER_IMAGE_SIZE',
                                     "big")
ARTICLE_PRIMARY_IMAGE_SIZE = getattr(settings,
                                     'NEWSROOM_ARTICLE_TEASER_IMAGE_SIZE',
                                     "extra_large")
CACHE_PERIOD = getattr(settings, 'NEWSROOM_CACHE_PERIOD', 500)
ADVERT_CODE = getattr(settings, 'NEWSROOM_ADVERT_CODE', '')
# ADVERT_CODE_1 = getattr(settings, 'NEWSROOM_ADVERT_CODE_1', '')
# ADVERT_CODE_2 = getattr(settings, 'NEWSROOM_ADVERT_CODE_2', '')
SUPPORT_US_IMAGES = getattr(settings, 'NEWSROOM_SUPPORT_US_IMAGES', [])

EDITOR = getattr(settings, 'ARTICLES_EDITOR', "")
INVOICE_EMAIL = getattr(settings, 'INVOICE_EMAIL', "")

SEARCH_RESULTS_PER_PAGE = getattr(settings, 'NEWSROOM_SEARCH_RESULTS_PER_PAGE',
                                  10)
MAX_SEARCH_RESULTS = getattr(settings, 'NEWSROOM_MAX_SEARCH_RESULTS', 50)

SEARCH_CONFIG = getattr(settings, 'NEWSROOM_SEARCH_CONFIG', 'english')

LOGO = getattr(settings, 'NEWSROOM_LOGO', 'newsroom/images/GroundUpLogo.png')
