import datetime
import logging
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import linebreaks
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site
from django.core.mail import send_mail
import sys
import pytz
import html2text
from newsroom.models import Article
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
            message = linebreaks(republisherarticle.republisher.message)
            if republisherarticle.note:
                message = message + linebreaks(republisherarticle.note)
            url = "http://" + Site.objects.all()[0].domain + \
                        republisherarticle.article.get_absolute_url()
            message = message + "<p>" + "URL: " + url + "</p>"
            message = message + "<p>Here is the article " \
                      "(it may be poorly formatted in email):</p>"
            message = message + "<h2>" + republisherarticle.article.title + \
                      "</h2>"
            if republisherarticle.article.subtitle:
                message = message + "<h3>" + \
                          republisherarticle.article.subtitle + "</h3>"
            message = message + "<p>Byline: "
            message = message + republisherarticle.article.cached_byline_no_links \
                      + "</p>"
            if republisherarticle.article.cached_primary_image:
                message = message + "<p>Primary Image:</p>"
                message = message + "<p>"
                message = message + "<img src='http://" +  \
                          Site.objects.all()[0].domain + \
                          republisherarticle.article.cached_primary_image + \
                          "'style='width:70%' /></p>"
                if republisherarticle.article.primary_image_caption:
                    message = message + "<p>Primary Image Caption: "
                    message = message + \
                              republisherarticle.article.primary_image_caption
                    message = message + "</p>"
            message = message + "<h3>Body of the article " \
                      "(images might not appear in email):</h3>"
            message = message + "<div>" + republisherarticle.article.body + \
                      "</div>"
            message = message + "<hr/><p>Originally published on " + \
                      "<a href='" + url + "'>GroundUp</a>. " \
                      "Copyright (C) GroundUp "  + str(timezone.now().year) + \
                      ". All rights reserved.</p>"
            subject = "Article from GroundUp: " + \
                      republisherarticle.article.title
            email_addresses = republisherarticle.republisher.email_addresses
            email_list = [address.strip() for address in \
                          email_addresses.split(",")]
            email_list.append(settings.REPUBLISHER_EMAIL_FROM)
            try:
                send_mail(subject, html2text.html2text(message),
                          settings.REPUBLISHER_EMAIL_FROM,
                          email_list, html_message=message, fail_silently=False)
                republisherarticle.status = "sent"
                republisherarticle.save()
                successes = successes + 1
                print("EmailRepublishers: Sent: {}". \
                      format(str(republisherarticle)))
            except:
                failures = failures + 1
                republisherarticle.status = "failed"
                republisherarticle.save()
                print("EmailRepublishers: Error: ", sys.exc_info()[0])
                print("EmailRepublishers: Failed send: {}". \
                      format(str(republisherarticle)))

    return {"successes" : successes, "failures" : failures}


class Command(BaseCommand):
    help = 'Sends articles to republishers'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("EmailRepublishers: {0}:".format(str(timezone.now())))
        success_dict = process()
        print("EmailRepublishers: Successful: {0}. Failed: {1}".\
              format(success_dict["successes"], success_dict["failures"]))
