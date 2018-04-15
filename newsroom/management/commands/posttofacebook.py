import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site
import sys
import facebook
from newsroom.models import Article
import traceback


def get_api(cfg):
    graph = facebook.GraphAPI(cfg['access_token'])
    return graph


def process(days, max_posts):
    cfg = {
        "page_id": settings.FACEBOOK_PAGE_ID,
        "access_token": settings.FACEBOOK_ACCESS_TOKEN,
    }
    successes = 0
    failures = 0
    try:
        api = get_api(cfg)
    except Exception as e:
        print("Exception message:", e)
        traceback.print_exc()
        print("PostToFacebook: Accessing Facebook failed.")
        print("PostToFacebook: Error: ", sys.exc_info()[0])
        return

    date_from = timezone.now() - datetime.timedelta(days=days)
    articles = Article.objects.published().filter(published__gte=date_from). \
        filter(facebook_send_status="scheduled")
    post_count = 0
    for article in articles:
        dont_send_before = article.published + \
                        datetime.timedelta(minutes=article.facebook_wait_time)
        if timezone.now() >= dont_send_before:
            post_count = post_count + 1
            if post_count > max_posts:
                break

        message = article.facebook_message
        link = "http://" + \
               Site.objects.all()[0].domain + article.get_absolute_url()
        attachment = {
            'link': link,
        }
        try:
            api.put_wall_post(message=message,
                              attachment=attachment)
            print("message: {}".format(message))
            print("attachment: {}".format(attachment))
            print("PostToFacebook: {}".format(article.title))
            successes = successes + 1
            article.facebook_send_status = "sent"
            article.save()
        except Exception as e:
            print("Exception message:", e)
            traceback.print_exc()
            failures = failures + 1
            article.facebook_send_status = "failed"
            print("PostToFacebook: Error: ", sys.exc_info()[0])
            print("PostToFacebook: Failed post: {}".format(article.title))
            article.save()

    return {"successes": successes, "failures": failures}


class Command(BaseCommand):
    help = 'Post scheduled articles to Facebook'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int,
                            help="Number of days back "
                            "in time to look for posts.")
        parser.add_argument('maxposts', type=int,
                            help="Maximum number of posts to send.")

    def handle(self, *args, **options):
        days = options["days"]
        max_posts = options["maxposts"]
        print("PostToFacebook: {0}: Processing {1} days "
              "with a maximum of {2} posts.".
              format(str(timezone.now()), days, max_posts))
        success_dict = process(days, max_posts)
        print("PostToFacebook: Successful: {0}. Failed: {1}".
              format(success_dict["successes"], success_dict["failures"]))
