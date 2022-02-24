import datetime
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site

import sys
import html2text
from newsroom.models import Correction
from republisher.models import RepublisherArticle, Republisher

def process(hours_back):
    successes = 0
    failures = 0

    start_time = timezone.now() - datetime.timedelta(hours=hours_back)
    corrections = Correction.objects.filter(created__gt=start_time). \
        filter(notify_republishers=True). \
        filter(publishers_notified=False)

    for correction in corrections:
        correction.publishers_notified = True
        correction.save()
        republisher_articles = RepublisherArticle.objects.\
            filter(article=correction.article).filter(status="sent"). \
            filter(modified__lt=correction.created).distinct()

        prefix = "https://" + Site.objects.all()[0].domain
        url = prefix + correction.article.get_absolute_url()
        # Send email to each of these republishers

        for republisher_article in republisher_articles:
            message = render_to_string('newsroom/notify_correction.html',
                                       {'republisher':
                                        republisher_article.republisher,
                                        'correction': correction,
                                        'URL': url})
            subject = "Article " + correction.get_update_type_display()
            email_addresses = republisher_article.republisher.email_addresses
            email_list = [address.strip() for address in
                          email_addresses.split(",")]
            email_list.append(settings.REPUBLISHER_EMAIL_FROM)
            try:
                send_mail(subject, html2text.html2text(message),
                          settings.REPUBLISHER_EMAIL_FROM,
                          email_list, html_message=message,
                          fail_silently=False)
                successes = successes + 1
                print("EmailRepublishers: Sent: {}".
                      format(str(republisher_article)))
            except:
                failures = failures + 1
                print("EmailRepublishers: Error: ", sys.exc_info()[0])
                print("EmailRepublishers: Failed send: {}".
                      format(str(republisher_article)))


    return {"successes": successes, "failures": failures}


class Command(BaseCommand):
    help = 'Sends corrections to republishers'

    def add_arguments(self, parser):
        parser.add_argument('hours_back', type=int,
                            help="Number of hours back to process.",
                            default=72)


    def handle(self, *args, **options):
        print("Email corrections: {}:".format(str(timezone.now())))
        success_dict = process(options['hours_back'])
        print("Email corrections: Successful: {0}. Failed: {1}".
              format(success_dict["successes"], success_dict["failures"]))
