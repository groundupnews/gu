from django.test import TestCase

from django.test import TestCase
from django.test import Client
from django.core import mail
from django.db import IntegrityError
from django.utils import timezone

from newsroom.models import Article, Topic, Category, Author

from payment.models import Invoice, Commission, Fund
from django.contrib.auth.models import User

from decimal import *

class InvoiceTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        fund = Fund()
        fund.name = "Bertha|Reporters"
        fund.save()

        category = Category()
        category.name = "News"
        category.slug = "news"
        category.save()


        author1 = Author()
        author1.first_names = "Joe"
        author1.last_name = "Bloggs"
        author1.email = "joe@example.com"
        author1.freelancer = True
        author1.save()
        author2 = Author()
        author2.first_names = "Jane"
        author2.last_name = "Doe"
        author2.email = "jane@example.com"
        author2.freelancer = True
        author2.save()
        author3 = Author()
        author3.first_names = "Lois"
        author3.last_name = "Lane"
        author3.email = "lane@example.com"
        author3.freelancer = False
        author3.save()

        article1 = Article()
        article1.title = "Test commission 1"
        article1.slug = "test-commission-1"
        article1.category = Category.objects.get(name="News")
        article1.published = timezone.now()
        article1.author_01 = author1
        article1.author_02 = author2
        article1.author_03 = author3
        article1.save()

        article2 = Article()
        article2.title = "Test commission 2"
        article2.slug = "test-commission-2"
        article2.category = Category.objects.get(name="News")
        article2.published = timezone.now()
        article2.author_01 = author1
        article2.save()

        article3 = Article()
        article3.title = "Test commission 3"
        article3.slug = "test-commission-3"
        article3.category = Category.objects.get(name="News")
        article3.published = timezone.now()
        article3.author_01 = author1
        article3.save()

        article4 = Article()
        article4.title = "Test commission 4"
        article4.slug = "test-commission-4"
        article4.category = Category.objects.get(name="News")
        article4.published = timezone.now()
        article4.author_01 = author1
        article4.author_02 = author2
        article4.save()

    def test_commissions(self):
        fund = Fund.objects.get(name="Bertha|Reporters")
        author1 = Author.objects.get(email="joe@example.com")
        author2 = Author.objects.get(email="jane@example.com")
        from django.core import management
        management.call_command('processinvoices')
        commissions = Commission.objects.all()
        self.assertEqual(len(commissions), 6)
        for commission in commissions:
            commission.commission_due = Decimal(900.00)
            commission.fund = fund
            commission.save()
        c = Commission.objects.filter(date_notified_approved__isnull=True)
        self.assertEqual(len(c), 6)

        invoices = Invoice.objects.filter(status="-")
        self.assertEqual(len(invoices), 2)
        for invoice in invoices:
            invoice.status = "0"
            invoice.save()

        management.call_command('processinvoices')
        c = Commission.objects.filter(date_notified_approved__isnull=True)
        self.assertEqual(len(c), 0)
        invoices = Invoice.objects.all()
        self.assertEqual(len(invoices), 2)
        invoices = Invoice.objects.filter(status="0")
        self.assertEqual(len(invoices), 2)
        invoices = Invoice.objects.filter(status="4")
        self.assertEqual(len(invoices), 0)
        invoices = Invoice.objects.filter(status="0")
        for invoice in invoices:
            invoice.status = "4"
            invoice.save()
        invoices = Invoice.objects.filter(status="4")
        self.assertEqual(len(invoices), 2)
        invoices = Invoice.objects.filter(date_notified_payment__isnull=True)
        self.assertEqual(len(invoices), 2)
        management.call_command('processinvoices')
        invoices = Invoice.objects.filter(date_notified_payment__isnull=False)
        self.assertEqual(len(invoices), 2)

        article5 = Article()
        article5.title = "Test commission 5"
        article5.slug = "test-commission-5"
        article5.category = Category.objects.get(name="News")
        article5.published = timezone.now()
        article5.author_01 = author1
        article5.author_02 = author2
        article5.save()

        management.call_command('processinvoices')
        invoices = Invoice.objects.filter(status="-")
        self.assertEqual(len(invoices), 2)
        for invoice in invoices:
            self.assertEqual(invoice.invoice_num, 2)
            invoice.status = "0"
            invoice.save()

        commissions = Commission.objects.filter(fund__isnull=True)
        self.assertEqual(len(commissions), 2)
        for commission in commissions:
            commission.commission_due = Decimal(900.00)
            commission.fund = fund
            commission.save()
        for invoice in invoices:
            invoice.status = "4"
        management.call_command('processinvoices')
        invoices = Invoice.objects.filter(date_notified_payment__isnull=True)
        self.assertEqual(len(invoices), 2)
        management.call_command('processinvoices')
        invoices = Invoice.objects.filter(date_notified_payment__isnull=False)
        self.assertEqual(len(invoices), 2)
        for email in mail.outbox:
            print("From:", email.from_email)
            print("To:", email.to)
            print("Subject:", email.subject)
            print("Body:", email.body)
