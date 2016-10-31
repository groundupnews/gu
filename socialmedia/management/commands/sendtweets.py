import datetime
import logging
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site
import sys
import tweepy
import pytz
from socialmedia.settings import TIME_BETWEEN_TWEETS
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
    successes = 0
    failures = 0
    try:
        api = get_api(cfg)
    except:
        print("Sendtweets: Accessing Twitter failed.")
        print("Sendtweets: Error: ", sys.exc_info()[0])
        return

    date_from = timezone.now() - datetime.timedelta(days=days)
    articles = Article.objects.published().filter(published__gte=date_from). \
               order_by("last_tweeted")
    tweet_count = 0

    for article in articles:
        tweets = article.tweet_set.filter(status="scheduled").order_by("wait_time")
        for tweet in tweets:

            dont_send_before = max(article.published + \
                                   datetime.timedelta(minutes=tweet.wait_time),
                                   article.last_tweeted + \
                                   datetime.timedelta(minutes=
                                                      TIME_BETWEEN_TWEETS))
            if timezone.now() >= dont_send_before:
                tweet_count = tweet_count + 1
                if tweet_count > max_tweets:
                    break

                text = tweet.tweet_text.strip()
                text += " " + "http://" + \
                        Site.objects.all()[0].domain + article.get_absolute_url()
                for handle in tweet.tag_accounts.all():
                    text += " @" + str(handle.name)
                try:
                    if tweet.image:
                        image_file = settings.MEDIA_ROOT + str(tweet.image)
                        api.update_with_media(filename=image_file, status=text)
                        print("Sendtweets: Sending tweet with image: {}".format(text))
                    else:
                        status = api.update_status(status=text)
                        print("Sendtweets: Sending tweet: {}".format(text))
                    tweet.status = "sent"
                    tweet.save()
                    article.last_tweeted = timezone.now()
                    article.save()
                    successes = successes + 1
                    break # Maximum of one successful tweet per article
                except:
                    failures = failures + 1
                    tweet.status = "failed"
                    print("Sendtweets: Error: ", sys.exc_info()[0])
                    print("Sendtweets: Failed tweet: {}".format(text))
                    tweet.save()

        if tweet_count > max_tweets:
            break
    return {"successes" : successes, "failures" : failures}


class Command(BaseCommand):
    help = 'Sends scheduled article tweets to Twitter'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int,
                            help="Number of days back in time to look for tweets.")
        parser.add_argument('maxtweets', type=int,
                            help="Maximum number of tweets to send.")

    def handle(self, *args, **options):
        days = options["days"]
        max_tweets = options["maxtweets"]
        print("Sendtweets: {0}: Processing {1} days with a maximum of {2} tweets.". \
              format(str(timezone.now()), days, max_tweets))
        success_dict = process(days, max_tweets)
        print("Sendtweets: Successful: {0}. Failed: {1}".\
              format(success_dict["successes"], success_dict["failures"]))
