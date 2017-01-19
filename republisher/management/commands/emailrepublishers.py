import datetime
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site
from django.core.mail import send_mail
import sys
import html2text
from bs4 import BeautifulSoup as bs
from republisher.models import RepublisherArticle


def process():
    successes = 0
    failures = 0

    republisherarticles = RepublisherArticle.objects.filter(status="scheduled")

    for republisherarticle in republisherarticles:
        # Only notify once article is published
        if not republisherarticle.article.is_published():
            continue
        # Check that sufficient time has passed since publishing
        dont_send_before = republisherarticle.article.published + \
            datetime.timedelta(minutes=republisherarticle.wait_time)
        if timezone.now() >= dont_send_before:
            prefix = "http://" + Site.objects.all()[0].domain
            url = prefix + republisherarticle.article.get_absolute_url()
            article = republisherarticle.article
            if article.cached_primary_image[0] == "/":
                article.cached_primary_image = prefix + \
                    article.cached_primary_image
            soup = bs(article.body, 'html.parser')
            images = soup.find_all("img")
            for image in images:
                if image['src'][0] == '/':
                    image['src'] = prefix + image['src']
            links = soup.find_all("a")
            for link in links:
                if 'href' in link and len(link['href']) > 0 and \
                                       link['href'][0] == '/':
                    link['href'] = prefix + link['href']
            article.body = str(soup)
            message = render_to_string('republisher/message.html',
                                       {'republisher':
                                        republisherarticle.republisher,
                                        'note': republisherarticle.note,
                                        'article':
                                        republisherarticle.article,
                                        'url': url})
            subject = "Article from GroundUp: " + \
                      republisherarticle.article.title
            email_addresses = republisherarticle.republisher.email_addresses
            email_list = [address.strip() for address in
                          email_addresses.split(",")]
            email_list.append(settings.REPUBLISHER_EMAIL_FROM)
            try:
                send_mail(subject, html2text.html2text(message),
                          settings.REPUBLISHER_EMAIL_FROM,
                          email_list, html_message=message,
                          fail_silently=False)
                republisherarticle.status = "sent"
                republisherarticle.save()
                successes = successes + 1
                print("EmailRepublishers: Sent: {}".
                      format(str(republisherarticle)))
            except:
                failures = failures + 1
                republisherarticle.status = "failed"
                republisherarticle.save()
                print("EmailRepublishers: Error: ", sys.exc_info()[0])
                print("EmailRepublishers: Failed send: {}".
                      format(str(republisherarticle)))

    return {"successes": successes, "failures": failures}


class Command(BaseCommand):
    help = 'Sends articles to republishers'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("EmailRepublishers: {0}:".format(str(timezone.now())))
        success_dict = process()
        print("EmailRepublishers: Successful: {0}. Failed: {1}".
              format(success_dict["successes"], success_dict["failures"]))
