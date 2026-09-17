import csv
import io
import shutil
import tempfile
from datetime import date
from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User, Permission
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from . import sars
from .forms import StaffCertificateForm
from .models import Donor, Donation, Currency, S18ACertificate
from .views import signer


def make_donation(donor, currency, when, amount, status="success"):
    return Donation.objects.create(
        donor=donor,
        currency_type=currency,
        amount=amount,
        status=status,
        datetime_of_donation=when,
    )


class PdfMockMixin:
    """stub out WeasyPrint and keep archived PDFs in a throwaway directory.

    approve() now renders and stores the issued PDF, so anything that
    approves a certificate needs both of these.
    """

    def setUp(self):
        super().setUp()
        patcher = mock.patch("donationPage.pdf.HTML")
        self.mock_pdf = patcher.start()
        rendered = self.mock_pdf.return_value.render.return_value
        rendered.pages = [mock.Mock()]
        rendered.write_pdf.return_value = b"%PDF-fake"
        self.addCleanup(patcher.stop)

        media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media, True)
        override = override_settings(MEDIA_ROOT=media)
        override.enable()
        self.addCleanup(override.disable)


class TaxYearAggregationTests(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(currency_abr="ZAR")
        self.donor = Donor.objects.create(
            name="Sandra Cleary", email="sandra@example.com",
            donor_url="sandra")

    def test_tax_year_period_boundaries(self):
        start, end = S18ACertificate.tax_year_period(2026)
        self.assertEqual(start, date(2025, 3, 1))
        self.assertEqual(end, date(2026, 2, 28))

    def test_tax_year_period_handles_leap_year(self):
        start, end = S18ACertificate.tax_year_period(2024)
        self.assertEqual(start, date(2023, 3, 1))
        self.assertEqual(end, date(2024, 2, 29))

    def test_tax_year_for_date(self):
        # march falls into the next year's tax year.
        self.assertEqual(
            S18ACertificate.tax_year_for_date(timezone.make_aware(
                timezone.datetime(2025, 3, 5))), 2026)
        # february falls into the current calendar year's tax year.
        self.assertEqual(
            S18ACertificate.tax_year_for_date(timezone.make_aware(
                timezone.datetime(2026, 2, 25))), 2026)

    def test_tax_year_for_date_uses_local_time(self):
        """00:30 on 1 March SAST is 22:30 on 28 February UTC. datetimes come
        back from the database in UTC, so we have to convert to local time
        before reading the tax year off them."""
        tz = timezone.get_current_timezone()
        make_donation(self.donor, self.currency, timezone.make_aware(
            timezone.datetime(2025, 3, 1, 0, 30), tz), 100)
        self.assertEqual(
            S18ACertificate.available_tax_years(self.donor), [2026])

        # ...and the donation is inside the period the certificate builds from.
        cert = S18ACertificate()
        cert.build_from_tax_year(self.donor, 2026)
        self.assertEqual(cert.amount, Decimal("100.00"))

    def test_build_from_tax_year_aggregates_only_successful_in_period(self):
        tz = timezone.get_current_timezone()
        # in period, successful
        make_donation(self.donor, self.currency,
                      timezone.make_aware(timezone.datetime(2025, 4, 1), tz), 100)
        make_donation(self.donor, self.currency,
                      timezone.make_aware(timezone.datetime(2025, 5, 1), tz), 200)
        # in period but failed - excluded
        make_donation(self.donor, self.currency,
                      timezone.make_aware(timezone.datetime(2025, 6, 1), tz),
                      999, status="failed")
        # outside period - excluded
        make_donation(self.donor, self.currency,
                      timezone.make_aware(timezone.datetime(2024, 1, 1), tz), 500)

        cert = S18ACertificate()
        cert.snapshot_from_donor(self.donor)
        donations = cert.build_from_tax_year(self.donor, 2026)
        cert.save()
        cert.donations.set(donations)

        self.assertEqual(cert.amount, Decimal("300.00"))
        self.assertEqual(cert.donations.count(), 2)
        self.assertEqual(cert.tax_year, 2026)

    def test_build_from_tax_year_totals_exactly(self):
        """Donation.amount is a float, so the certificate total shouldn't
        inherit binary rounding error from it."""
        tz = timezone.get_current_timezone()
        for _ in range(3):
            make_donation(self.donor, self.currency,
                          timezone.make_aware(timezone.datetime(2025, 4, 1), tz),
                          0.1)
        cert = S18ACertificate()
        cert.build_from_tax_year(self.donor, 2026)
        self.assertEqual(cert.amount, Decimal("0.30"))

    def test_available_tax_years(self):
        tz = timezone.get_current_timezone()
        make_donation(self.donor, self.currency,
                      timezone.make_aware(timezone.datetime(2025, 4, 1), tz), 100)
        make_donation(self.donor, self.currency,
                      timezone.make_aware(timezone.datetime(2026, 5, 1), tz), 100)
        self.assertEqual(
            S18ACertificate.available_tax_years(self.donor), [2027, 2026])


class ReceiptNumberTests(PdfMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user("staff", password="x")
        self.donor = Donor.objects.create(
            name="Test", email="t@example.com", donor_url="t")

    def _cert(self):
        c = S18ACertificate()
        c.snapshot_from_donor(self.donor)
        c.save()
        return c

    def test_first_number_starts_at_setting(self):
        with self.settings(S18A_RECEIPT_START=332):
            self.assertEqual(S18ACertificate.allocate_receipt_number(), 332)

    def test_numbers_increment_and_do_not_reuse(self):
        c1 = self._cert()
        c1.approve(self.user)
        c2 = self._cert()
        c2.approve(self.user)
        self.assertEqual(c2.receipt_number, c1.receipt_number + 1)

    def test_approve_sets_status_signatory_and_marks_donations(self):
        currency = Currency.objects.create(currency_abr="ZAR")
        donation = make_donation(
            self.donor, currency, timezone.now(), 100)
        cert = self._cert()
        cert.donations.set([donation])
        cert.approve(self.user)

        self.assertEqual(cert.status, S18ACertificate.STATUS_APPROVED)
        self.assertIsNotNone(cert.receipt_number)
        self.assertIsNotNone(cert.signatory_date)
        self.assertEqual(cert.approved_by, self.user)
        donation.refresh_from_db()
        self.assertTrue(donation.section18a_issued)

    def test_approve_archives_the_issued_pdf(self):
        cert = self._cert()
        cert.approve(self.user)
        cert.refresh_from_db()
        self.assertTrue(cert.pdf_file)
        self.assertEqual(cert.pdf_file.read(), b"%PDF-fake")

        # later renders serve the archived bytes, not a fresh render, so a
        # template or logo change can't alter an issued receipt.
        self.mock_pdf.reset_mock()
        from .pdf import certificate_pdf_bytes
        self.assertEqual(certificate_pdf_bytes(cert), b"%PDF-fake")
        self.assertFalse(self.mock_pdf.called)


class CertificateRequestTests(PdfMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.currency = Currency.objects.create(currency_abr="ZAR")
        self.donor = Donor.objects.create(
            name="Sandra Cleary", email="sandra@example.com",
            donor_url="sandra")
        tz = timezone.get_current_timezone()
        self.donation = make_donation(
            self.donor, self.currency,
            timezone.make_aware(timezone.datetime(2025, 4, 1), tz), 250)
        self.token = signer.sign(self.donor.donor_url)

    def _url(self):
        return "/donation/donations/certificate/request/{}/".format(self.token)

    def _post_data(self, **overrides):
        data = {
            'name': "Sandra Cleary",
            'email': "sandra@example.com",
            'nature_of_donor': "natural_person",
            'id_type': "sa_id",
            'id_country': "South Africa",
            'id_number': "8001015009087",
            'address': "1 Main Road, Cape Town",
            'tax_year': "2026",
        }
        data.update(overrides)
        return data

    def test_request_page_renders(self):
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name="date_of_birth"')

    def test_invalid_token_rejected(self):
        resp = self.client.get(
            "/donation/donations/certificate/request/not-a-token/")
        self.assertEqual(resp.status_code, 400)

    def test_request_creates_certificate_and_saves_donor_details(self):
        resp = self.client.post(self._url(), self._post_data(), follow=True)
        self.assertEqual(resp.status_code, 200)

        cert = S18ACertificate.objects.get()
        self.assertTrue(cert.requested_by_donor)
        self.assertEqual(cert.status, S18ACertificate.STATUS_PENDING)
        self.assertEqual(cert.tax_year, 2026)
        self.assertEqual(cert.amount, Decimal("250.00"))
        self.assertEqual(list(cert.donations.all()), [self.donation])
        self.assertIsNone(cert.receipt_number)

        # SARS details get saved back onto the donor for reuse.
        self.donor.refresh_from_db()
        self.assertEqual(self.donor.id_number, "8001015009087")
        self.assertEqual(self.donor.address, "1 Main Road, Cape Town")

        # staff get notified.
        self.assertEqual(len(mail.outbox), 1)

    def test_sars_fields_are_required(self):
        resp = self.client.post(
            self._url(), self._post_data(id_number="", address=""))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(S18ACertificate.objects.exists())
        form = resp.context['form']
        self.assertIn('id_number', form.errors)
        self.assertIn('address', form.errors)

    def test_country_of_issue_required_only_for_natural_persons(self):
        resp = self.client.post(self._url(), self._post_data(id_country=""))
        self.assertIn('id_country', resp.context['form'].errors)

        resp = self.client.post(self._url(), self._post_data(
            nature_of_donor="company", id_type="registration",
            id_country=""), follow=True)
        self.assertTrue(S18ACertificate.objects.exists())

    def test_date_of_birth_required_without_a_south_african_id(self):
        """SARS keys a natural person on their ID number, or their date of
        birth when they have none."""
        resp = self.client.post(self._url(), self._post_data(
            id_type="passport", id_number="A1234567", id_country="Ireland"))
        self.assertIn('date_of_birth', resp.context['form'].errors)
        self.assertFalse(S18ACertificate.objects.exists())

        self.client.post(self._url(), self._post_data(
            id_type="passport", id_number="A1234567", id_country="Ireland",
            date_of_birth="1980-03-14"), follow=True)
        cert = S18ACertificate.objects.get()
        self.assertEqual(cert.date_of_birth, date(1980, 3, 14))
        # saved on the donor too, so it's prefilled next time.
        self.donor.refresh_from_db()
        self.assertEqual(self.donor.date_of_birth, date(1980, 3, 14))

    def test_date_of_birth_not_required_with_a_south_african_id(self):
        self.client.post(self._url(), self._post_data(), follow=True)
        cert = S18ACertificate.objects.get()
        self.assertIsNone(cert.date_of_birth)

    def test_date_of_birth_not_required_for_an_entity(self):
        self.client.post(self._url(), self._post_data(
            nature_of_donor="trust", id_type="trust_number",
            id_number="IT0593/96", id_country=""), follow=True)
        self.assertTrue(S18ACertificate.objects.exists())

    def test_duplicate_request_is_flagged_not_blocked(self):
        self.client.post(self._url(), self._post_data(), follow=True)
        self.client.post(self._url(), self._post_data(), follow=True)

        self.assertEqual(S18ACertificate.objects.count(), 2)
        newest = S18ACertificate.objects.first()
        self.assertIn("Possible duplicate", newest.staff_notes)
        self.assertIn("[possible duplicate]", mail.outbox[-1].subject)


class DonorCertificateDownloadTests(PdfMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user("staff", password="x")
        self.donor = Donor.objects.create(
            name="Test Donor", email="donor@example.com", donor_url="d")
        self.token = signer.sign(self.donor.donor_url)
        self.cert = S18ACertificate()
        self.cert.snapshot_from_donor(self.donor)
        self.cert.save()

    def _url(self, cert=None, token=None):
        return "/donation/donations/certificate/{}/pdf/{}/".format(
            (cert or self.cert).pk, token or self.token)

    def test_pending_certificate_is_not_downloadable(self):
        self.assertEqual(self.client.get(self._url()).status_code, 404)

    def test_donor_can_download_own_approved_certificate(self):
        self.cert.approve(self.staff)
        resp = self.client.get(self._url())
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertIn("attachment", resp["Content-Disposition"])
        self.assertEqual(b"".join(resp.streaming_content
                                  if resp.streaming else [resp.content]),
                         b"%PDF-fake")

    def test_other_donors_certificate_is_not_reachable(self):
        other = Donor.objects.create(
            name="Someone Else", email="other@example.com", donor_url="o")
        self.cert.approve(self.staff)
        resp = self.client.get(self._url(token=signer.sign(other.donor_url)))
        self.assertEqual(resp.status_code, 404)

    def test_dashboard_links_to_the_certificate(self):
        self.cert.approve(self.staff)
        resp = self.client.get(
            "/donation/donations/donor-dashboard/{}/".format(self.token))
        self.assertContains(resp, self._url())

    def test_filename_is_safe_for_a_header(self):
        from .pdf import certificate_filename
        self.cert.donor_name = 'Bad "Name"\r\nX-Injected: yes'
        self.cert.receipt_number = 332
        name = certificate_filename(self.cert)
        for char in '"\r\n':
            self.assertNotIn(char, name)


class CertificateWorkflowViewTests(PdfMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.donor = Donor.objects.create(
            name="Test Donor", email="donor@example.com", donor_url="d")
        self.cert = S18ACertificate()
        self.cert.snapshot_from_donor(self.donor)
        self.cert.save()

        self.staff = User.objects.create_user("staff", password="x")
        perm = Permission.objects.get(codename="change_s18acertificate")
        self.staff.user_permissions.add(perm)

    def _email_url(self):
        return "/donation/donations/certificates/{}/email/".format(self.cert.pk)

    def test_email_requires_approval(self):
        self.client.login(username="staff", password="x")
        self.client.post(self._email_url(), {'mode': 'standard'}, follow=True)
        self.cert.refresh_from_db()
        self.assertNotEqual(self.cert.status, S18ACertificate.STATUS_EMAILED)
        self.assertEqual(len(mail.outbox), 0)

    def test_non_staff_cannot_view_list(self):
        User.objects.create_user("plain", password="x")
        self.client.login(username="plain", password="x")
        resp = self.client.get("/donation/donations/certificates/")
        self.assertEqual(resp.status_code, 404)

    def test_pdf_view_renders(self):
        self.client.login(username="staff", password="x")
        resp = self.client.get(
            "/donation/donations/certificates/{}/pdf/".format(self.cert.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertTrue(self.mock_pdf.called)

    def test_approval_does_not_email_the_donor(self):
        """approving allocates the receipt number and archives the PDF -
        sending is a separate, deliberate step."""
        self.client.login(username="staff", password="x")
        self.client.post(
            "/donation/donations/certificates/{}/approve/".format(self.cert.pk),
            follow=True)

        self.cert.refresh_from_db()
        self.assertEqual(self.cert.status, S18ACertificate.STATUS_APPROVED)
        self.assertIsNotNone(self.cert.receipt_number)
        self.assertTrue(self.cert.pdf_file)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_page_offers_the_standard_wording(self):
        self.cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        resp = self.client.get(self._email_url())
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Thank you for your generous support",
                      resp.context['standard_body'])
        # the customisable form starts from the same wording.
        self.assertEqual(resp.context['form'].initial['message'],
                         resp.context['standard_body'])
        self.assertEqual(len(mail.outbox), 0)

    def test_standard_email_sends_and_marks(self):
        self.cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        self.client.post(self._email_url(), {'mode': 'standard'}, follow=True)

        self.cert.refresh_from_db()
        self.assertEqual(self.cert.status, S18ACertificate.STATUS_EMAILED)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ["donor@example.com"])
        self.assertEqual(len(sent.attachments), 1)
        self.assertIn("Section 18A", sent.subject)
        self.assertIn("Thank you for your generous support", sent.body)
        # html alternative alongside a plain-text body.
        self.assertTrue(sent.alternatives)
        self.assertNotIn("<p>", sent.body)
        self.assertIn("<p>", sent.alternatives[0][0])

    def test_custom_email_uses_the_edited_wording(self):
        self.cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        self.client.post(self._email_url(), {
            'mode': 'custom',
            'subject': "Your 2026 receipt, as discussed",
            'message': "Hi Test\n\nHere it is at last.",
        }, follow=True)

        self.cert.refresh_from_db()
        self.assertEqual(self.cert.status, S18ACertificate.STATUS_EMAILED)
        sent = mail.outbox[0]
        self.assertEqual(sent.subject, "Your 2026 receipt, as discussed")
        self.assertEqual(sent.body, "Hi Test\n\nHere it is at last.")
        self.assertNotIn("generous support", sent.alternatives[0][0])
        # the PDF still goes with it.
        self.assertEqual(len(sent.attachments), 1)

    def test_custom_email_requires_a_subject_and_message(self):
        self.cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        resp = self.client.post(self._email_url(), {
            'mode': 'custom', 'subject': "", 'message': ""})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('subject', resp.context['form'].errors)
        self.assertIn('message', resp.context['form'].errors)
        self.assertEqual(len(mail.outbox), 0)

    def test_send_failure_keeps_the_certificate_approved(self):
        self.cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        with mock.patch("donationPage.views.EmailMultiAlternatives.send",
                        side_effect=Exception("smtp down")):
            resp = self.client.post(self._email_url(), {'mode': 'standard'})

        self.assertEqual(resp.status_code, 200)
        self.cert.refresh_from_db()
        self.assertEqual(self.cert.status, S18ACertificate.STATUS_APPROVED)

    def test_issued_certificate_contents_are_locked_except_staff_notes(self):
        self.cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        resp = self.client.get(
            "/donation/donations/certificates/{}/".format(self.cert.pk))
        form = resp.context['form']
        for locked in form.Meta.fields:
            if locked == 'staff_notes':
                self.assertFalse(form.fields[locked].disabled)
                continue
            self.assertTrue(form.fields[locked].disabled)

    def test_issued_certificate_content_cannot_be_changed(self):
        self.cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        self.client.post(
            "/donation/donations/certificates/{}/".format(self.cert.pk), {
                'contact_email': 'attacker@example.com',
                'nature_of_donation': 'Something else',
                'signatory_name': 'Different signer',
                'staff_notes': 'Checked after issue',
            }, follow=True)

        self.cert.refresh_from_db()
        self.assertEqual(self.cert.contact_email, 'donor@example.com')
        self.assertEqual(self.cert.nature_of_donation, 'Cash (via EFT)')
        self.assertEqual(self.cert.signatory_name, 'Nathan Geffen')
        self.assertEqual(self.cert.staff_notes, 'Checked after issue')

    def test_issued_certificate_cannot_be_rejected(self):
        self.cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        self.client.post(
            "/donation/donations/certificates/{}/reject/".format(self.cert.pk),
            {'reason': 'Too late'}, follow=True)

        self.cert.refresh_from_db()
        self.assertEqual(self.cert.status, S18ACertificate.STATUS_APPROVED)

    def test_pending_certificate_can_be_rejected(self):
        self.client.login(username="staff", password="x")
        self.client.post(
            "/donation/donations/certificates/{}/reject/".format(self.cert.pk),
            {'reason': 'Incomplete details'}, follow=True)

        self.cert.refresh_from_db()
        self.assertEqual(self.cert.status, S18ACertificate.STATUS_REJECTED)
        self.assertEqual(self.cert.rejection_reason, 'Incomplete details')

    def test_certificate_form_requires_a_date_of_birth_without_an_sa_id(self):
        self.client.login(username="staff", password="x")
        base = {
            'donor_name': "Aoife Ni Bhriain",
            'nature_of_donor': "natural_person",
            'id_type': "passport",
            'id_number': "A1234567",
            'id_country': "Ireland",
            'amount': "500.00",
            'nature_of_donation': "Cash (via EFT)",
            'signatory_name': "Nathan Geffen",
            'signatory_title': "Director",
        }
        resp = self.client.post("/donation/donations/certificates/new/", base)
        self.assertIn('date_of_birth', resp.context['form'].errors)

        self.client.post("/donation/donations/certificates/new/",
                         dict(base, date_of_birth="1980-03-14"), follow=True)
        cert = S18ACertificate.objects.get(donor_name="Aoife Ni Bhriain")
        self.assertEqual(cert.date_of_birth, date(1980, 3, 14))

    def test_staff_created_certificate_links_its_donations(self):
        currency = Currency.objects.create(currency_abr="ZAR")
        tz = timezone.get_current_timezone()
        donation = make_donation(
            self.donor, currency,
            timezone.make_aware(timezone.datetime(2025, 4, 1), tz), 100)

        self.client.login(username="staff", password="x")
        self.client.post("/donation/donations/certificates/new/", {
            'donor': self.donor.pk,
            'donor_name': self.donor.name,
            'tax_year': 2026,
            'period_start': "2025-03-01",
            'period_end': "2026-02-28",
            'amount': "100.00",
            'nature_of_donation': "Cash (via EFT)",
            'signatory_name': "Nathan Geffen",
            'signatory_title': "Director",
        }, follow=True)

        cert = S18ACertificate.objects.exclude(pk=self.cert.pk).get()
        self.assertEqual(list(cert.donations.all()), [donation])
        cert.approve(self.staff)
        donation.refresh_from_db()
        self.assertTrue(donation.section18a_issued)


class SarsCsvTests(PdfMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user("staff", password="x")
        self.staff.user_permissions.add(
            Permission.objects.get(codename="change_s18acertificate"))

    def _cert(self, **kwargs):
        defaults = {
            'donor_name': "Adv Robert Olaf Petersen",
            'nature_of_donor': "natural_person",
            'id_type': "sa_id",
            'id_number': "490110 5729 086",
            'income_tax_ref': "2481 084 032",
            'contact_number': "082 978 1183",
            'contact_email': "rop1949@example.com",
            'address': ("809 St Martini Gardens\n74 Queen Victoria Street\n"
                        "Gardens, Cape Town\nWestern Cape\n8001"),
            'tax_year': 2026,
            'amount': Decimal("10000.00"),
            'nature_of_donation': "Cash (via EFT)",
            'date_of_donation_text': "17 February 2026",
            'signatory_date': date(2026, 2, 20),
        }
        defaults.update(kwargs)
        return S18ACertificate.objects.create(**defaults)

    def test_row_matches_the_submission_layout(self):
        cert = self._cert()
        cert.approve(self.staff)
        self.assertEqual(sars.row(cert), [
            '',
            cert.receipt_number,
            "20 February 2026",
            "Adv Robert Olaf",
            "Petersen",
            "Natural Person",
            "490110 5729 086",
            "",
            "2481 084 032",
            "082 978 1183",
            "rop1949@example.com",
            "809 St Martini Gardens",
            "74 Queen Victoria Street",
            "Gardens, Cape Town",
            "Western Cape",
            "8001",
            "Cash (via EFT)",
            "R10 000,00",
            "17 February 2026",
        ])
        self.assertEqual(len(sars.row(cert)), len(sars.COLUMNS))

    def test_entity_name_stays_whole(self):
        cert = self._cert(donor_name="The Inglis Family Charitable Trust",
                          nature_of_donor="trust", id_type="trust_number")
        self.assertEqual(cert.first_names_display,
                         "The Inglis Family Charitable Trust")
        self.assertEqual(cert.surname_display, "")

    def test_name_override_wins_over_the_split(self):
        cert = self._cert(donor_name="Jan van der Merwe",
                          first_names="Jan", surname="van der Merwe")
        self.assertEqual(cert.first_names_display, "Jan")
        self.assertEqual(cert.surname_display, "van der Merwe")

    def test_surname_override_alone_does_not_duplicate_names(self):
        cert = self._cert(donor_name="Jan van der Merwe",
                          surname="van der Merwe")
        self.assertEqual(cert.first_names_display, "")
        self.assertEqual(cert.surname_display, "van der Merwe")

    def test_single_word_natural_person_name(self):
        cert = self._cert(donor_name="Sandra")
        self.assertEqual(cert.first_names_display, "Sandra")
        self.assertEqual(cert.surname_display, "")

    def test_date_of_birth_gets_its_own_column(self):
        cert = self._cert(id_type="passport", id_number="A1234567",
                          date_of_birth=date(1980, 3, 14))
        row = sars.row(cert)
        self.assertEqual(row[sars.COLUMNS.index('Date of Birth')],
                         "14 March 1980")
        self.assertEqual(row[sars.COLUMNS.index('IDNumber')], "A1234567")

    def test_amount_uses_rand_formatting(self):
        self.assertEqual(sars.format_amount(Decimal("1500000")), "R1 500 000,00")
        self.assertEqual(sars.format_amount(Decimal("600")), "R600,00")
        self.assertEqual(sars.format_amount(None), "R0,00")

    def test_short_address_is_padded_and_long_one_folded(self):
        self.assertEqual(sars.address_lines("72 Arum Avenue\nKommetjie\n7975"),
                         ["72 Arum Avenue", "Kommetjie", "7975", "", ""])
        self.assertEqual(sars.address_lines("a\nb\nc\nd\ne\nf\ng"),
                         ["a", "b", "c", "d", "e, f, g"])
        self.assertEqual(sars.address_lines(""), [""] * 5)

    def test_date_of_issue_falls_back_to_the_approval_date(self):
        cert = self._cert(signatory_date=None)
        self.assertIsNone(cert.date_of_issue)
        cert.approve(self.staff)
        # approve() stamps the signatory date - that's what shows up on the receipt.
        self.assertEqual(cert.date_of_issue, cert.signatory_date)

    def _download(self, query=""):
        self.client.login(username="staff", password="x")
        resp = self.client.get(
            "/donation/donations/certificates/export.csv" + query)
        self.assertEqual(resp.status_code, 200)
        text = resp.content.decode("utf-8-sig")
        return resp, list(csv.reader(io.StringIO(text)))

    def test_export_contains_only_issued_certificates(self):
        issued = self._cert()
        issued.approve(self.staff)
        self._cert(donor_name="Still A Draft")  # never approved, so it shouldn't show up

        resp, rows = self._download()
        self.assertEqual(rows[0], sars.COLUMNS)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], str(issued.receipt_number))
        self.assertIn("attachment", resp["Content-Disposition"])
        # the BOM is there so excel actually reads the file as UTF-8.
        self.assertTrue(resp.content.startswith(b"\xef\xbb\xbf"))

    def test_export_excludes_rejected_receipts_left_by_legacy_data(self):
        issued = self._cert()
        issued.approve(self.staff)
        rejected = self._cert(
            donor_name="Voided legacy receipt",
            status=S18ACertificate.STATUS_REJECTED,
            receipt_number=9999)

        _, rows = self._download()
        exported_numbers = {row[1] for row in rows[1:]}
        self.assertIn(str(issued.receipt_number), exported_numbers)
        self.assertNotIn(str(rejected.receipt_number), exported_numbers)

    def test_export_respects_the_tax_year_filter(self):
        old = self._cert(tax_year=2025)
        old.approve(self.staff)
        new = self._cert(tax_year=2026)
        new.approve(self.staff)

        resp, rows = self._download("?tax_year=2026")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], str(new.receipt_number))
        self.assertIn("groundup-s18a-2026.csv", resp["Content-Disposition"])

    def test_export_ignores_a_junk_tax_year(self):
        cert = self._cert()
        cert.approve(self.staff)
        resp, rows = self._download('?tax_year="; rm -rf /')
        self.assertEqual(len(rows), 2)
        self.assertIn("groundup-s18a-all.csv", resp["Content-Disposition"])

    def test_export_is_ordered_by_receipt_number(self):
        for name in ("C", "A", "B"):
            self._cert(donor_name=name).approve(self.staff)
        _, rows = self._download()
        numbers = [int(row[1]) for row in rows[1:]]
        self.assertEqual(numbers, sorted(numbers))

    def test_list_page_offers_the_export_for_the_current_filters(self):
        cert = self._cert()
        cert.approve(self.staff)
        self.client.login(username="staff", password="x")
        resp = self.client.get(
            "/donation/donations/certificates/?tax_year=2026&status=approved")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(list(resp.context['tax_years']), [2026])
        self.assertEqual(resp.context['tax_year'], 2026)
        self.assertEqual(list(resp.context['page_obj']), [cert])
        self.assertContains(resp, "export.csv?status=approved&amp;tax_year=2026")

    def test_non_staff_cannot_export(self):
        User.objects.create_user("plain", password="x")
        self.client.login(username="plain", password="x")
        resp = self.client.get(
            "/donation/donations/certificates/export.csv")
        self.assertEqual(resp.status_code, 404)


class CertificateSearchTests(PdfMockMixin, TestCase):
    """Staff searching the certificate list, and the donor dropdown."""

    def setUp(self):
        super().setUp()
        self.staff = User.objects.create_user("staff", password="x")
        self.staff.user_permissions.add(
            Permission.objects.get(codename="change_s18acertificate"))
        self.client.login(username="staff", password="x")
        self.zulu = Donor.objects.create(
            name="Thandi Zulu", email="thandi@example.com", donor_url="z")
        self.abrahams = Donor.objects.create(
            name="Riedwaan Abrahams", email="riedwaan@example.com",
            donor_url="a")

    def _cert(self, donor, **kwargs):
        certificate = S18ACertificate(donor=donor, tax_year=2026,
                                      amount=Decimal("100.00"))
        certificate.snapshot_from_donor(donor)
        for key, value in kwargs.items():
            setattr(certificate, key, value)
        certificate.save()
        return certificate

    def _search(self, query):
        resp = self.client.get(
            "/donation/donations/certificates/", {'q': query})
        self.assertEqual(resp.status_code, 200)
        return list(resp.context['page_obj'])

    def test_search_matches_the_donor_name(self):
        zulu = self._cert(self.zulu)
        self._cert(self.abrahams)
        self.assertEqual(self._search("zulu"), [zulu])

    def test_search_matches_the_donor_email(self):
        self._cert(self.zulu)
        abrahams = self._cert(self.abrahams)
        self.assertEqual(self._search("riedwaan@example.com"), [abrahams])

    def test_search_matches_a_receipt_number(self):
        zulu = self._cert(self.zulu)
        zulu.approve(self.staff)
        self._cert(self.abrahams)
        self.assertEqual(self._search(str(zulu.receipt_number)), [zulu])

    def test_search_survives_paging_and_the_export_link(self):
        self._cert(self.zulu)
        resp = self.client.get(
            "/donation/donations/certificates/", {'q': "zulu"})
        self.assertContains(resp, "export.csv?status=&amp;tax_year=&amp;q=zulu")

    def test_no_search_leaves_the_list_alone(self):
        certificates = {self._cert(self.zulu), self._cert(self.abrahams)}
        self.assertEqual(set(self._search("")), certificates)

    def test_donor_dropdown_is_ordered_by_surname(self):
        form = StaffCertificateForm()
        labels = [label for value, label in form.fields['donor'].choices
                  if value]
        self.assertEqual(labels, [
            "Riedwaan Abrahams (riedwaan@example.com)",
            "Thandi Zulu (thandi@example.com)",
        ])

    def test_a_donor_picked_from_the_dropdown_still_validates(self):
        form = StaffCertificateForm({
            'donor': self.zulu.pk,
            'donor_name': self.zulu.name,
            'amount': "100.00",
            'nature_of_donation': "Cash (via EFT)",
            'signatory_name': "Nathan Geffen",
            'signatory_title': "Director",
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['donor'], self.zulu)
