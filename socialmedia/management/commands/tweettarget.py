import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site
import sys
import tweepy
import traceback
from target.models import Target


def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)


def process_new(days, max_tweets):
    cfg = {
        "consumer_key": settings.TWITTER_CONSUMER_KEY,
        "consumer_secret": settings.TWITTER_CONSUMER_SECRET,
        "access_token": settings.TWITTER_ACCESS_TOKEN,
        "access_token_secret": settings.TWITTER_TOKEN_SECRET
    }
    successes = 0
    failures = 0
    try:
        api = get_api(cfg)
    except Exception as e:
        print("Exception message:", e)
        traceback.print_exc()
        print("Sendtweets: Accessing Twitter failed.")
        print("Sendtweets: Error: ", sys.exc_info()[0])
        return

    date_from = timezone.now() - datetime.timedelta(days=days)
    targets = Target.objects.published().\
        filter(published__gte=date_from).\
        filter(tweeted=False).\
        exclude(tweet_text="")
    print("Targets:", targets)
    tweet_count = 0

    for target in targets:
        text = target.tweet_text.strip() + " https://" + \
            Site.objects.all()[0].domain + \
            target.get_absolute_url()
        image_file = settings.MEDIA_ROOT + "targets/target_" + str(target.pk) + \
            ".png"
        try:
            media = api.media_upload(image_file)
            api.update_status(text, media_ids=[media.media_id, ])
            print("TweetNewTargets: Sending target tweet", target.number)
            successes = successes + 1
            target.tweeted = True
            target.save()
        except Exception as e:
            print("Exception message:", e)
            traceback.print_exc()
            failures = failures + 1
            print("TweetNewTargets: Error: ", sys.exc_info()[0])
            print("TweetNewTargets: Failed tweet: {}".format(text))
        if tweet_count > max_tweets:
            break
    return {"successes": successes, "failures": failures}

def process_solution(days, max_tweets):
    return {"successes": 0, "failures": 0}

class Command(BaseCommand):
    help = 'Sends scheduled article tweets to Twitter'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int,
                            help="Number of days back "
                            "in time to look for tweets.")
        parser.add_argument('maxtweets', type=int,
                            help="Maximum number of tweets to send.")

    def handle(self, *args, **options):
        days = options["days"]
        max_tweets = options["maxtweets"]
        print("TweetNewTargets: {0}: Processing {1} days with "
              "a maximum of {2} tweets.".
              format(str(timezone.now()), days, max_tweets))
        success_dict = process_new(days, max_tweets)
        print("TweetNewTargets: Successful: {0}. Failed: {1}".
              format(success_dict["successes"], success_dict["failures"]))

        if success_dict['successes'] < max_tweets:
            success_dict = process_solution(days, max_tweets)
