from django.conf import settings

ARTICLE_COPYRIGHT = getattr(settings, 'NEWSROOM_ARTICLE_COPYRIGHT', "")
ARTICLES_PER_PAGE = getattr(settings, 'NEWSROOM_ARTICLES_PER_PAGE', 16)
BEAUTIFUL_SOUP_PARSER = getattr(settings, 'NEWSROOM_BEAUTIFUL_SOUP_PARSER',
                                "lxml")
ARTICLE_SUMMARY_IMAGE_SIZE = getattr(settings,
                                     'NEWSROOM_ARTICLE_TEASER_IMAGE_SIZE',
                                     "LEAVE")
ARTICLE_PRIMARY_IMAGE_SIZE = getattr(settings,
                                     'NEWSROOM_ARTICLE_TEASER_IMAGE_SIZE',
                                     "extra_large")
CACHE_PERIOD = getattr(settings, 'NEWSROOM_CACHE_PERIOD', 10 * 60)
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
SEARCH_MAXLEN = getattr(settings, 'NEWSROOM_SEARCH_MAXLEN', 60)

LOGO = getattr(settings, 'NEWSROOM_LOGO', 'newsroom/images/GroundUpLogo.png')

VIDEOS_PER_PAGE = getattr(settings, 'NEWSROOM_VIDEOS_PER_PAGE', 12)
VIDEOS_ON_HOME = getattr(settings, 'NEWSROOM_VIDEOS_ON_HOME', 4)
YOUTUBE_CHANNEL_URL = getattr(settings, 'NEWSROOM_YOUTUBE_CHANNEL_URL',
                              'https://www.youtube.com/@GroundUpNews')
VIDEOS_INTRO = getattr(
    settings, 'NEWSROOM_VIDEOS_INTRO',
    'Every GroundUp video is free to watch.')

VIDEO_DEFAULT_BYLINE = getattr(settings, 'NEWSROOM_VIDEO_DEFAULT_BYLINE',
                               'GroundUp Video Team')

VIDEO_LICENCE_URL = getattr(settings, 'NEWSROOM_VIDEO_LICENCE_URL',
                            'https://groundup.org.za/licencing/detail/2/')
VIDEO_COPYRIGHT = getattr(settings, 'NEWSROOM_VIDEO_COPYRIGHT', '')

FOLLOW_LINKS = getattr(settings, 'NEWSROOM_FOLLOW_LINKS', [
    {'name': 'YouTube', 'url': YOUTUBE_CHANNEL_URL, 'icon': 'icon-youtube'},
    {'name': 'TikTok', 'url': 'https://www.tiktok.com/@groundup_news',
     'icon': 'icon-tiktok'},
    {'name': 'Instagram', 'url': 'https://www.instagram.com/groundup_news/',
     'icon': 'icon-instagram'},
    {'name': 'Facebook', 'url': 'https://www.facebook.com/GroundUpNews/',
     'icon': 'icon-facebook'},
    {'name': 'X', 'url': 'https://twitter.com/GroundUp_News',
     'icon': 'icon-twitter'},
    {'name': 'Bluesky', 'url': 'https://bsky.app/profile/groundup.org.za',
     'icon': 'icon-bluesky'},
    {'name': 'WhatsApp',
     'url': 'https://whatsapp.com/channel/0029Vah4OJcK0IBgG4CUkz35',
     'icon': 'icon-whatsapp'},
    {'name': 'Newsletter', 'url': 'https://eepurl.com/Or2a9',
     'icon': 'icon-mail'},
])
