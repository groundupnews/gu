from django.conf import settings
TIME_BETWEEN_TWEETS = getattr(settings, 'SOCIAL_MEDIA_TIME_BETWEEN_TWEETS', 90)
