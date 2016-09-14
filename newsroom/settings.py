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
                                     "large")
CACHE_PERIOD = getattr(settings, 'NEWSROOM_CACHE_PERIOD', 500)
ADVERT_CODE = getattr(settings, 'NEWSROOM_ADVERT_CODE', '')
EDITOR = getattr(settings, 'ARTICLES_EDITOR', "")
