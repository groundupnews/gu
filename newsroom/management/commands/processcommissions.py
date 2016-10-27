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

from newsroom.models import Article, Author, Commission

def generate_commissions():
    num_commissions = 0
    articles = Article.objects.published().filter(commissions_processed=False)

    for article in articles:
        process_commissions = False
        if article.override_commissions_system == "NO":
            if article.category is not "Opinion":
                process_commissions = True
        elif article.override_commissions_system == "PROCESS":
                process_commissions = True

        if process_commissions is True:
            authors = [article.author_01, article.author_02, article.author_03,
                       article.author_04, article.author_05]
            for author in authors:
                if author is not None and author.freelancer is True:
                    commission = Commission()
                    commission.author = author
                    commission.article = article
                    commission.description = "System generated possible commission."
                    commission.sys_generated = True
                    commission.date_generated = timezone.now()
                    num_commissions = num_commissions + 1
                    commission.save()

        article.commissions_processed = True
        article.save()
    return num_commissions

def notify_freelancers():
    num_processed = 0
    num_approved = 0
    commissions = Commission.objects.filter(date_approved__isnull=False).\
                  filter(date_notified_approved__isnull=True)
    for commission in commissions:
        subject = "Payment approved for work done for GroundUp"
        message = render_to_string('newsroom/commission_approved.txt',
                                   {'commission': commission})
        if commission.commission_due > 0.00:
            try:
                print("ProcessCommissions: Emailing approval: ", \
                      commission.author.email,\
                      " about ", commission.pk)
                send_mail(subject,
                          message,
                          settings.INVOICE_EMAIL,
                          [commission.author.email, settings.INVOICE_EMAIL,]
                )
            except SMTPException as err:
                print("ProcessCommission: Error sending approval "
                      "email: {0} - {1}".\
                      format(commission.author.email, err))
        commission.date_notified_approved = timezone.now()
        commission.save()
        num_approved = num_approved + 1

    commissions = Commission.objects.filter(date_processed__isnull=False).\
                  filter(date_notified_processed__isnull=True)
    for commission in commissions:
        subject = "Payment processed for work done for GroundUp"
        message = render_to_string('newsroom/commission_processed.txt',
                                   {'commission': commission})
        if commission.commission_due > 0.00:
            try:
                print("ProcessCommissions: Emailing processed: ", \
                      commission.author.email,\
                      " about ", commission.pk)
                send_mail(subject,
                          message,
                          settings.INVOICE_EMAIL,
                          [commission.author.email, settings.INVOICE_EMAIL,]
                )
            except SMTPException as err:
                print("ProcessCommissions: Error sending processed"
                      "email: {0} - {1}".\
                      format(commission.author.email, err))
        commission.date_notified_processed = timezone.now()
        commission.save()
        num_processed = num_processed + 1
    return (num_approved, num_processed,)

def process():
    num_commissions = generate_commissions()
    (num_approved, num_processed,) = notify_freelancers()
    return (num_commissions, num_approved, num_processed,)


class Command(BaseCommand):
    help = 'Process possible commissions for freelancer articles.'

    def handle(self, *args, **options):
        results = process()
        print("ProcessCommissions: Commissions: {0}. Processed: {1}. "\
              "Approved: {2}".\
              format(results[0], results[1], results[2],))
