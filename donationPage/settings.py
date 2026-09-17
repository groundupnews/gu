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


S18A_PBO = getattr(settings, 'DONATION_S18A_PBO', {
    'name': 'GroundUp News NPC',
    'address_lines': [
        'Belmont Office Park',
        'Rondebosch | Cape Town | 7700',
    ],
    'website': 'www.groundup.org.za',
    'phone': '+27 (0)21 788 9163',
    'registration': 'Registration 2020/428260/08 | 254-625 NPO | PBO 930071956',
})

# addresses notified when a donor requests a certificate.
STAFF_EMAILS = getattr(settings, 'S18A_STAFF_EMAILS', ['donations@groundup.org.za'])

EMAIL_SUBJECT = getattr(
    settings, 'S18A_EMAIL_SUBJECT',
    "Your GroundUp Section 18A donation tax certificate")
