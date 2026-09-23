import datetime
from decimal import *

from django.contrib.auth.models import User
from django.core import mail
from django.db import IntegrityError
from django.test import Client, TestCase
from django.utils import timezone
from django.urls import reverse
from newsroom.models import (Article, Author, Category, Topic, Video,
                            VideoContributor)
from payment.forms import CommissionForm
from payment.models import (Commission, Fund, Invoice, RateCard,
                            create_video_payments)


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
        rate_card.date_from = timezone.make_aware(
            timezone.datetime(2020, 1, 1), timezone.get_current_timezone()
        )
        rate_card.bonus= 530.00
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


class VideoPaymentTest(TestCase):
    """A video is billable in its own right: the people who make one are not
    the authors of an article."""

    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(
            first_names="Ashraf", last_name="Hendricks",
            email="ashraf@example.com", freelancer="f",
        )
        cls.fund = Fund.objects.create(name="Bertha|Video")
        cls.video = Video.objects.create(
            title="Municipal debt explained",
            slug="municipal-debt-explained",
            youtube_id="5RI7cF6A-8Q",
            published=timezone.now(),
        )
        cls.staff = User.objects.create_superuser(
            "boss", "boss@example.com", "abcde"
        )

    def make_payment(self):
        commission = Commission.create_commission(self.author)
        commission.video = self.video
        commission.description = "Video contributor"
        commission.notes = "Camera"
        commission.commission_due = Decimal(1620.00)
        commission.fund = self.fund
        commission.save()
        return commission

    def test_a_payment_can_be_for_a_video(self):
        commission = self.make_payment()
        self.assertEqual(list(self.video.payments.all()), [commission])
        self.assertEqual(commission.work(), self.video)
        self.assertIn("Municipal debt explained", str(commission))
        self.assertEqual(commission.estimate_payment()["total"], 0.00)

    def test_deleting_a_video_keeps_the_payment(self):
        commission = self.make_payment()
        self.video.delete()
        commission.refresh_from_db()
        self.assertIsNone(commission.video)
        self.assertEqual(commission.commission_due, Decimal("1620.0000"))

    def test_the_video_is_named_on_the_invoice(self):
        commission = self.make_payment()
        self.client.force_login(self.staff)
        response = self.client.get(
            reverse("payments:invoice.detail",
                    args=[self.author.pk, commission.invoice.invoice_num])
        )
        self.assertContains(response, "Municipal debt explained")
        self.assertContains(response, self.video.get_absolute_url())
        self.assertContains(response, "Article or video")

    def test_the_new_payment_form_is_prefilled_from_a_video(self):
        self.client.force_login(self.staff)
        response = self.client.get(
            "{}?author={}&video={}".format(
                reverse("payments:commissions.detail.add"),
                self.author.pk, self.video.pk)
        )
        self.assertEqual(response.status_code, 200)
        fields = response.context["form"].fields
        self.assertEqual(fields["video"].initial, self.video.pk)
        self.assertEqual(fields["author"].initial, self.author.pk)
        self.assertEqual(fields["description"].initial, "Video contributor")

    def test_a_payment_is_for_an_article_or_a_video_but_not_both(self):
        category = Category.objects.create(name="News", slug="news")
        article = Article.objects.create(
            title="Pyramid scheme collapse", slug="pyramid-scheme-collapse",
            category=category, published=timezone.now(),
        )
        form = CommissionForm(data={
            "author": str(self.author.pk),
            "article": str(article.pk),
            "video": str(self.video.pk),
            "description": "Video contributor",
            "commission_due": "1620.00",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("one article or one video", str(form.errors))


class VideoPaymentAutomationTest(TestCase):
    """Publishing a video raises the payment items for its credits"""

    @classmethod
    def setUpTestData(cls):
        cls.reporter = Author.objects.create(
            first_names="Barbara", last_name="Maregele",
            email="barbara@example.com", freelancer="f",
        )
        cls.camera = Author.objects.create(
            first_names="Ashraf", last_name="Hendricks",
            email="ashraf@example.com", freelancer="f",
        )
        cls.unpaid = Author.objects.create(
            first_names="Never", last_name="Paid",
            email="never@example.com", freelancer="n",
        )
        cls.fund = Fund.objects.create(name="Bertha|Video")

    def make_video(self, published=True):
        return Video.objects.create(
            title="Municipal debt explained",
            slug="municipal-debt-explained",
            youtube_id="5RI7cF6A-8Q",
            published=timezone.now() if published else None,
        )

    def items_for(self, video, author):
        return Commission.objects.filter(video=video, invoice__author=author)

    def test_publishing_raises_one_item_per_person(self):
        video = self.make_video()
        VideoContributor.objects.create(video=video, author=self.reporter,
                                        roles="reporting")
        VideoContributor.objects.create(video=video, author=self.camera,
                                        roles="camera")
        items = Commission.objects.filter(video=video)
        self.assertEqual(items.count(), 2)
        item = self.items_for(video, self.camera).get()
        self.assertEqual(item.description, "Video contributor")
        self.assertEqual(item.notes, "Camera")
        self.assertTrue(item.sys_generated)
        self.assertEqual(item.invoice.author, self.camera)
        self.assertEqual(item.invoice.status, "-")

    def test_two_jobs_for_one_person_is_one_item_naming_both(self):
        video = self.make_video()
        VideoContributor.objects.create(video=video, author=self.camera,
                                        roles="camera,editing")
        item = self.items_for(video, self.camera).get()
        self.assertEqual(item.notes, "Camera, Video editing")

    def test_a_job_added_later_lands_on_the_item_already_there(self):
        video = self.make_video()
        credit = VideoContributor.objects.create(video=video,
                                                 author=self.camera,
                                                 roles="camera")
        credit.roles = "camera,editing"
        credit.save()
        item = self.items_for(video, self.camera).get()
        self.assertEqual(item.notes, "Camera, Video editing")

    def test_nothing_is_raised_twice(self):
        video = self.make_video()
        VideoContributor.objects.create(video=video, author=self.reporter,
                                        roles="reporting")
        item = self.items_for(video, self.reporter).get()
        item.commission_due = Decimal(1620.00)
        item.save()
        video.title = "Municipal debt explained, again"
        video.save()
        video.save()
        self.assertEqual(self.items_for(video, self.reporter).count(), 1)
        self.assertEqual(create_video_payments(video), [])
        # The amount an editor typed is untouched.
        self.assertEqual(
            self.items_for(video, self.reporter).get().commission_due,
            Decimal("1620.0000"),
        )

    def test_a_draft_raises_nothing_until_it_is_published(self):
        video = self.make_video(published=False)
        VideoContributor.objects.create(video=video, author=self.reporter,
                                        roles="reporting")
        self.assertEqual(Commission.objects.filter(video=video).count(), 0)
        # A future date is not published either.
        video.published = timezone.now() + datetime.timedelta(days=1)
        video.save()
        self.assertEqual(Commission.objects.filter(video=video).count(), 0)
        video.published = timezone.now()
        video.save()
        self.assertEqual(Commission.objects.filter(video=video).count(), 1)

    def test_a_credit_added_after_publication_is_paid(self):
        video = self.make_video()
        self.assertEqual(Commission.objects.filter(video=video).count(), 0)
        VideoContributor.objects.create(video=video, author=self.camera,
                                        roles="camera")
        self.assertEqual(self.items_for(video, self.camera).count(), 1)

    def test_someone_marked_do_not_pay_is_left_out(self):
        video = self.make_video()
        VideoContributor.objects.create(video=video, author=self.camera,
                                        roles="camera", no_payment=True)
        self.assertEqual(Commission.objects.filter(video=video).count(), 0)

    def test_the_invoices_system_skips_anyone_it_never_pays(self):
        video = self.make_video()
        VideoContributor.objects.create(video=video, author=self.unpaid,
                                        roles="presenting")
        self.assertEqual(Commission.objects.filter(video=video).count(), 0)

    def test_marking_do_not_pay_afterwards_withdraws_an_untouched_item(self):
        video = self.make_video()
        contributor = VideoContributor.objects.create(
            video=video, author=self.camera, roles="camera")
        contributor.no_payment = True
        contributor.save()
        item = Commission.objects.get(video=video)
        self.assertTrue(item.deleted)
        # And it does not come back on the next save of the video.
        video.save()
        self.assertEqual(Commission.objects.filter(video=video).count(), 1)

    def test_one_person_marked_do_not_pay_leaves_the_others_paid(self):
        video = self.make_video()
        VideoContributor.objects.create(video=video, author=self.camera,
                                        roles="camera,editing")
        staffer = VideoContributor.objects.create(video=video,
                                                  author=self.reporter,
                                                  roles="reporting")
        staffer.no_payment = True
        staffer.save()
        item = Commission.objects.get(video=video, deleted=False)
        self.assertEqual(item.invoice.author, self.camera)
        self.assertEqual(item.notes, "Camera, Video editing")

    def test_a_priced_or_approved_item_is_never_withdrawn(self):
        video = self.make_video()
        contributor = VideoContributor.objects.create(
            video=video, author=self.camera, roles="camera")
        item = Commission.objects.get(video=video)
        item.commission_due = Decimal(1620.00)
        item.fund = self.fund
        item.save()
        contributor.no_payment = True
        contributor.save()
        item.refresh_from_db()
        self.assertFalse(item.deleted)

    def test_removing_a_credit_withdraws_an_untouched_item(self):
        video = self.make_video()
        contributor = VideoContributor.objects.create(
            video=video, author=self.camera, roles="camera,editing")
        VideoContributor.objects.create(
            video=video, author=self.reporter, roles="reporting")
        contributor.delete()
        self.assertTrue(
            Commission.objects.get(video=video,
                                   invoice__author=self.camera).deleted)
        # The other person on the video is untouched.
        self.assertFalse(
            Commission.objects.get(video=video,
                                   invoice__author=self.reporter).deleted)

    def test_deleting_the_video_leaves_the_payments_alone(self):
        video = self.make_video()
        VideoContributor.objects.create(video=video, author=self.camera,
                                        roles="camera")
        video.delete()
        item = Commission.objects.get(invoice__author=self.camera)
        self.assertIsNone(item.video)
        self.assertFalse(item.deleted)


    def test_reassigning_credit_withdraws_the_previous_unpriced_payment(self):
        video = self.make_video()
        credit = VideoContributor.objects.create(video=video, author=self.camera, roles="camera")
        credit.author = self.reporter
        credit.save()
        self.assertTrue(self.items_for(video, self.camera).get().deleted)
        self.assertFalse(self.items_for(video, self.reporter).get().deleted)

    def test_reassigning_credit_preserves_a_priced_payment(self):
        video = self.make_video()
        credit = VideoContributor.objects.create(video=video, author=self.camera, roles="camera")
        item = self.items_for(video, self.camera).get()
        item.commission_due = Decimal("100")
        item.save()
        credit.author = self.reporter
        credit.save()
        item.refresh_from_db()
        self.assertFalse(item.deleted)
        self.assertEqual(item.commission_due, Decimal("100"))

    def test_invoice_job_catches_scheduled_videos_without_another_save(self):
        from unittest.mock import patch
        from payment.management.commands.processinvoices import generate_commissions
        video = self.make_video(published=False)
        video.published = timezone.now() + datetime.timedelta(days=1)
        video.save()
        VideoContributor.objects.create(video=video, author=self.camera, roles="camera")
        self.assertFalse(self.items_for(video, self.camera).exists())
        with patch("django.utils.timezone.now", return_value=video.published + datetime.timedelta(seconds=1)):
            self.assertEqual(generate_commissions(), 1)
            self.assertEqual(generate_commissions(), 0)
        self.assertEqual(self.items_for(video, self.camera).count(), 1)
