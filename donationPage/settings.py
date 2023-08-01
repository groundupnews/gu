from django.conf import settings


BEAUTIFUL_SOUP_PARSER = getattr(settings, 'NEWSROOM_BEAUTIFUL_SOUP_PARSER',
                                "lxml")
CACHE_PERIOD = getattr(settings, 'NEWSROOM_CACHE_PERIOD', 10 * 60)
#ADVERT_CODE = getattr(settings, 'NEWSROOM_ADVERT_CODE', '')

SUPPORT_US_IMAGES = getattr(settings, 'NEWSROOM_SUPPORT_US_IMAGES', [])

#EDITOR = getattr(settings, 'ARTICLES_EDITOR', "")


#SEARCH_RESULTS_PER_PAGE = getattr(settings, 'NEWSROOM_SEARCH_RESULTS_PER_PAGE',
#                                  10)
#MAX_SEARCH_RESULTS = getattr(settings, 'NEWSROOM_MAX_SEARCH_RESULTS', 50)
#SEARCH_CONFIG = getattr(settings, 'NEWSROOM_SEARCH_CONFIG', 'english')
#SEARCH_MAXLEN = getattr(settings, 'NEWSROOM_SEARCH_MAXLEN', 60)

LOGO = getattr(settings, 'NEWSROOM_LOGO', 'newsroom/images/GroundUpLogo.png')
