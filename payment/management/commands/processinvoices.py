from smtplib import SMTPException
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.db import transaction

import datetime
import logging
from django.utils import timezone
from newsroom import settings

from newsroom.models import Article, Author
from payment.models import Commission, Invoice

def generate_commissions():
    num_commissions = 0
    articles = Article.objects.published().filter(commissions_processed=False)

    for article in articles:
        with transaction.atomic():
            process_commissions = False
            if article.override_commissions_system == "NO":
                if article.category.name is not "Opinion":
                    process_commissions = True
            elif article.override_commissions_system == "PROCESS":
                    process_commissions = True

            if process_commissions is True:
                authors = [article.author_01, article.author_02,
                           article.author_03, article.author_04,
                           article.author_05]
                for author in authors:
                    if author is not None and author.freelancer is True:
                        commission = Commission()
                        # commission.author = author
                        commission.article = article
                        commission.sys_generated = True
                        commission.date_generated = timezone.now()
                        num_commissions = num_commissions + 1
                        # Get the invoice for this commission
                        commission.invoice = Invoice.\
                                             get_open_invoice_for_author(author)
                        commission.save()

            article.commissions_processed = True
            article.save()
    return num_commissions

def notify_freelancers():
    site = Site.objects.get_current()
    num_approved = 0
    num_paid = 0
    # First do notifications for open invoices with approved commissions
    invoices = Invoice.objects.filter(status="0")
    for invoice in invoices:
        # Commissions for this invoice that are approved and
        # for which the author hasn't been notified
        commissions = Commission.objects.for_authors().\
                      filter(invoice=invoice).\
                      filter(date_notified_approved__isnull=True)

        if len(commissions) > 0:
            # Now we have to get all the commissions for this invoice
            commissions_all = Commission.objects.filter(invoice=invoice).\
                          filter(fund__isnull=False)
            # The template handles a bunch of different views and this is
            # the format it needs the commissions in because of those
            # other views.
            commissionformset = zip(commissions_all, range(len(commissions_all)))
            try:
                print("ProcessInvoices: Emailing approval: ", \
                      invoice.author.email,\
                      " about ", invoice.pk)
                subject = "Invoice for work done for GroundUp"
                message = render_to_string('payment/invoice_approved.txt',
                                           {'invoice': invoice,
                                            'commissionformset':
                                            commissionformset,
                                            'site' : site})
                send_mail(subject,
                          message,
                          settings.INVOICE_EMAIL,
                          [invoice.author.email, settings.INVOICE_EMAIL,],
                          html_message=message
                )
            except SMTPException as err:
                print("ProcessInvoices: Error sending approval "
                      "email: {0} - {1}".\
                      format(commission.author.email, err))
        for commission in commissions:
            commission.date_notified_approved = timezone.now()
            commission.save()

        num_approved = num_approved + 1

    # Second do notifications for paid invoices
    # Get all unnotified paid invoices
    invoices = Invoice.objects.filter(status="4").\
               filter(date_notified_payment__isnull=True)
    for invoice in invoices:
        # Get the approved commissions > 0.00 for this invoice
        commissions = Commission.objects.for_authors().\
                      filter(invoice=invoice).\
                      exclude(commission_due=0.00)
        commissionformset = zip(commissions, range(len(commissions)))

        subject = "Payment processed for work done for GroundUp"
        message = render_to_string('payment/invoice_paid.txt',
                                   {'invoice': invoice,
                                    'commissionformset': commissionformset,
                                    'site': site})

        print("ProcessInvoices: Emailing paid: ", \
              invoice.author.email,\
              " about ", invoice.pk)
        try:
                send_mail(subject,
                          message,
                          settings.INVOICE_EMAIL,
                          [invoice.author.email, settings.INVOICE_EMAIL,],
                          html_message=message
                )
        except SMTPException as err:
            print("ProcessInvoices: Error sending processed"
                  "email: {0} - {1}".\
                  format(commission.author.email, err))
        invoice.date_notified_payment = timezone.now()
        invoice.save()
        num_paid = num_paid + 1
    return (num_approved, num_paid,)

def process():
    num_commissions = generate_commissions()
    (num_approved, num_processed,) = notify_freelancers()
    return (num_commissions, num_approved, num_processed,)


class Command(BaseCommand):
    help = 'Process payments for freelancer articles.'

    def handle(self, *args, **options):
        results = process()
        print("ProcessInvoices: Commissions: {0}. "
              "Notifications of invoices with approved commissions: {1}. "\
              "Notifications of invoices paid: {2}".\
              format(results[0], results[1], results[2],))
