from decimal import *

from django.contrib.auth.models import User
from django.core import mail
from django.db import IntegrityError
from django.test import Client, TestCase
from django.utils import timezone
from django.urls import reverse
from newsroom.models import Article, Author, Category, Topic
from payment.models import Commission, Fund, Invoice, RateCard


class InvoiceTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        fund = Fund()
        fund.name = "Bertha|Reporters"
        fund.save()

        category = Category()
        category.name = "Video"
        category.slug = "video"
        category.save()

        category = Category()
        category.name = "News"
        category.slug = "news"
        category.save()


        author1 = Author()
        author1.first_names = "Joe"
        author1.last_name = "Bloggs"
        author1.email = "joe@example.com"
        author1.freelancer = "f"
        author1.save()
        author2 = Author()
        author2.first_names = "Jane"
        author2.last_name = "Doe"
        author2.email = "jane@example.com"
        author2.freelancer = "c"
        author2.save()
        author3 = Author()
        author3.first_names = "Lois"
        author3.last_name = "Lane"
        author3.email = "lane@example.com"
        author3.freelancer = "n"
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
        article3.author_02 = author2
        article3.save()

        article4 = Article()
        article4.title = "Test commission 4"
        article4.slug = "test-commission-4"
        article4.category = Category.objects.get(name="News")
        article4.published = timezone.now()
        article4.author_01 = author1
        article4.author_02 = author2
        article4.save()

        article5 = Article()
        article5.title = "Test commission 5"
        article5.slug = "test-commission-5"
        article5.category = Category.objects.get(name="News")
        article5.published = timezone.now()
        article5.author_01 = author1
        article5.author_02 = author2
        article5.save()

        article6 = Article()
        article6.title = "Test commission 6"
        article6.slug = "test-commission-6"
        article6.category = Category.objects.get(name="News")
        article6.published = timezone.now()
        article6.author_01 = author1
        article6.author_02 = author2
        article6.save()

        article7 = Article()
        article7.title = "Test commission 7"
        article7.slug = "test-commission-7"
        article7.category = Category.objects.get(name="News")
        article7.published = timezone.now()
        article7.author_01 = author2
        article7.author_02 = author1
        article7.save()

        article8 = Article()
        article8.title = "Test commission 8"
        article8.slug = "test-commission-8"
        article8.category = Category.objects.get(name="News")
        article8.published = timezone.now()
        article8.author_01 = author2
        article8.author_02 = author1
        article8.save()

        article9 = Article()
        article9.title = "Test commission 9"
        article9.slug = "test-commission-9"
        article9.category = Category.objects.get(name="News")
        article9.published = timezone.now()
        article9.author_01 = author2
        article9.author_02 = author1
        article9.save()

        article10 = Article()
        article10.title = "Test commission 10"
        article10.slug = "test-commission-10"
        article10.category = Category.objects.get(name="News")
        article10.published = timezone.now()
        article10.author_01 = author2
        article10.save()

        article20 = Article()
        article20.title = "Test commission 20"
        article20.slug = "test-commission-20"
        article20.category = Category.objects.get(name="Video")
        article20.published = timezone.now()
        article20.author_01 = author2
        article20.save()

        rate_card = RateCard()
        rate_card.allowance = 500.00
        rate_card.date_from = timezone.datetime(2020,1,1)
        rate_card.bonus_bonus = 530.00
        rate_card.bonus_articles = 4
        rate_card.save()

    def test_commissions(self):
        fund = Fund.objects.get(name="Bertha|Reporters")
        author1 = Author.objects.get(email="joe@example.com")
        author2 = Author.objects.get(email="jane@example.com")
        from django.core import management
        management.call_command('processinvoices')
        commissions = Commission.objects.all()
        self.assertEqual(len(commissions), 18)
        for commission in commissions:
            commission.commission_due = Decimal(900.00)
            commission.fund = fund
            commission.save()
        c = Commission.objects.filter(date_notified_approved__isnull=True)
        self.assertEqual(len(c), 18)

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

        article11 = Article()
        article11.title = "Test commission 11"
        article11.slug = "test-commission-11"
        article11.category = Category.objects.get(name="News")
        article11.published = timezone.now()
        article11.author_01 = author1
        article11.author_02 = author2
        article11.save()

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

        commissions = Commission.objects.filter(
            invoice__author__last_name="Bloggs")
        #commissions[4] is a known bonus commission and so here we confirm that it is reading the non-default value of 530
        self.assertEqual(commissions[0].estimate_bonus(), 530)
        #remove this loop, this is printing what the estimates are for each commission
        for c in commissions:
                print(c.estimate_bonus())
        num_bonuses = len([True for c in commissions if c.estimate_bonus() > 0])
        self.assertEqual(num_bonuses, 3)

        commissions = Commission.objects.filter(invoice__author__last_name="Doe")
        num_bonuses = len([True for c in commissions if c.estimate_bonus() > 0])
        self.assertEqual(num_bonuses, 0)

        user = User.objects.create_user('admin', 'admin@example.com', 'abcde')
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        c = Client()
        response = c.login(username='admin', password='abcde')
        self.assertEqual(response, True)
        url = reverse('payments:invoice.list')
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        url = '/invoices/2000/1/2020/9/0/'
        response = c.get(url)
        self.assertEqual(response.status_code, 200)

        invoice = Invoice.objects.all()[0]
        response = c.get('/invoices/' + str(invoice.author.pk) + '-' +
                         str(invoice.invoice_num))
        self.assertEqual(response.status_code, 200)
        response = c.get('/invoices/print/' + str(invoice.author.pk) + '-' +
                         str(invoice.invoice_num))
        self.assertEqual(response.status_code, 200)
        commission = Commission.objects.all()[0]
        response = c.get('/commissions/' + str(commission.pk))
        self.assertEqual(response.status_code, 200)
        response = c.get('/commissions/add')
        self.assertEqual(response.status_code, 200)
        response = c.get('/commissions/analysis')
        self.assertEqual(response.status_code, 200)

    def test_allowance(self):
        author = Author.objects.get(email="joe@example.com")
        print(author)
        self.assertEqual(Commission.can_bill_allowance(author), False)
        author.allowance = True
        author.save()
        self.assertEqual(Commission.can_bill_allowance(author), True)
        Commission.create_allowance(author)
        self.assertEqual(Commission.can_bill_allowance(author), False)
