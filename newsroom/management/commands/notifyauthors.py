from smtplib import SMTPException
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

import datetime
import logging
from django.utils import timezone
from newsroom import settings

from newsroom.models import Article, Author

def process(days_back, hours_since):
    successes = 0
    failures = 0
    base_url = "http://" + Site.objects.all()[0].domain
    date_from = timezone.now() - datetime.timedelta(days=days_back)
    date_to = timezone.now() - datetime.timedelta(hours=hours_since)
    articles = Article.objects.published().filter(published__gte=date_from). \
               filter(published__lte=date_to).filter(notified_authors=False)
    for article in articles:
        for author in [article.author_01, article.author_02, \
                       article.author_03, article.author_04, article.author_05]:
            if author and author.email is not None and author.email is not "":
                subject = "Your article has been published: " + article.title
                message = render_to_string('newsroom/published_article.txt',
                                           {'article': article,
                                            'author': author,
                                            'base_url': base_url})
                try:
                    print("NotifyAuthors: Emailing: ", author.email,\
                          " about ", article.title)
                    send_mail(
                        subject,
                        message,
                        settings.EDITOR,
                        [author.email]
                    )
                    successes = successes + 1
                except SMTPException as err:
                    print("Error sending email: {0} - {1}".\
                          format(author.email, err))
                    failures = failures + 1
        article.notified_authors = True
        article.save()
    return {'successes': successes, 'failures': failures}

class Command(BaseCommand):
    help = 'Notify authors that their articles have been posted.'

    def add_arguments(self, parser):
        parser.add_argument('days_back', type=int,
                            help="Number of days back in time to look for posts.")
        parser.add_argument('hours_since', type=int,
                            help="Number of hours to wait before sending.")

    def handle(self, *args, **options):
        days_back = options["days_back"]
        hours_since = options["hours_since"]
        print("NotifyWriters: {0}: Processing {1} days, waiting {2} hours.". \
              format(str(timezone.now()), days_back, hours_since))
        success_dict = process(days_back, hours_since)
        print("NotifyWriters: Successful: {0}. Failed: {1}".\
              format(success_dict["successes"], success_dict["failures"]))
