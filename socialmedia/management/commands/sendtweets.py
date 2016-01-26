import datetime
import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings
import sys
import tweepy
import pytz
from newsroom.models import Article


def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)

def process(days, max_tweets):
    cfg = {
        "consumer_key"        : settings.TWITTER_CONSUMER_KEY,
        "consumer_secret"     : settings.TWITTER_CONSUMER_SECRET,
        "access_token"        : settings.TWITTER_ACCESS_TOKEN,
        "access_token_secret" : settings.TWITTER_TOKEN_SECRET
    }

    date_from = timezone.now() - datetime.timedelta(days=days)
    articles = Article.objects.published().filter(published__gte=date_from)

    tweet_count = 0
    for article in articles:
        tweets = article.tweet_set.filter(status="scheduled").order_by("wait_time")
        for tweet in tweets:

            dont_send_before = article.published + \
                               datetime.timedelta(minutes=tweet.wait_time)
            if timezone.now() >= dont_send_before:
                tweet_count = tweet_count + 1
                if tweet_count > max_tweets:
                    break

                text = tweet.tweet_text
                text += " " + "http://" + \
                        Site.objects.all()[0].domain + article.get_absolute_url()
                for handle in tweet.tag_accounts.all():
                    text += " @" + str(handle.name)
                try:
                    api = get_api(cfg)
                    if tweet.image:
                        image_file = settings.MEDIA_ROOT + str(tweet.image)
                        api.update_with_media(filename=image_file, status=text)
                        print("Sending tweet with image: {}".format(text))
                    else:
                        status = api.update_status(status=text)
                        print("Sending tweet: {}".format(text))
                    tweet.status = "sent"
                    break # Maximum of one successful tweet per article
                except:
                    tweet.status = "failed"
                    print("Error: ", sys.exc_info()[0])
                    print("Failed tweet: {}".format(text))
                tweet.save()

        if tweet_count > max_tweets:
            break



class Command(BaseCommand):
    help = 'Hack to fix disqus ids for articles imported from Drupal'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int)
        parser.add_argument('maxtweets', type=int)

    def handle(self, *args, **options):
        days = options["days"]
        max_tweets = options["maxtweets"]
        print("Processing {0} days with a maximum of {1} tweets.". \
              format(days, max_tweets))
        process(days, max_tweets)
