# Generated using Claude.ai. Nathan corrected one of the tests and improved the
# code slightly.

from datetime import date
from dateutil.relativedelta import relativedelta

from django.test import TestCase, Client
from django.urls import reverse

from .models import Licence, Licensee, Contract, one_year_from_today
from republisher.models import Republisher

# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def make_licence(**kwargs):
    defaults = {"name": "CC BY 4.0", "text": "Some licence text", "notes": ""}
    defaults.update(kwargs)
    return Licence.objects.create(**defaults)


def make_republisher(name="Test Republisher"):
    """Return a minimal Republisher instance.  Adjust the import path and
    required fields to match your actual republisher app."""
    return Republisher.objects.create(name=name)


def make_licensee(republisher=None, licence=None, **kwargs):
    if republisher is None:
        republisher = make_republisher()
    if licence is None:
        licence = make_licence()
    return Licensee.objects.create(republisher=republisher, licence=licence, **kwargs)


def make_contract(licensee=None, **kwargs):
    if licensee is None:
        licensee = make_licensee()
    return Contract.objects.create(licensee=licensee, **kwargs)


# ===========================================================================
# one_year_from_today
# ===========================================================================


class OneYearFromTodayTests(TestCase):
    def test_returns_date_object(self):
        result = one_year_from_today()
        self.assertIsInstance(result, date)

    def test_one_day_before_one_year_from_now(self):
        expected = date.today() + relativedelta(years=1) - relativedelta(days=1)
        self.assertEqual(one_year_from_today(), expected)

    def test_not_exactly_one_year(self):
        exactly_one_year = date.today() + relativedelta(years=1)
        self.assertNotEqual(one_year_from_today(), exactly_one_year)


# ===========================================================================
# Licence model
# ===========================================================================


class LicenceModelTests(TestCase):
    def test_create_minimal_licence(self):
        licence = make_licence(name="MIT")
        self.assertIsNotNone(licence.pk)

    def test_str(self):
        licence = make_licence(name="Apache 2.0")
        self.assertEqual(str(licence), "Apache 2.0")

    def test_name_unique(self):
        from django.db import IntegrityError

        make_licence(name="Unique Licence")
        with self.assertRaises(IntegrityError):
            make_licence(name="Unique Licence")

    def test_text_blank_allowed(self):
        licence = make_licence(name="No Text", text="")
        self.assertEqual(licence.text, "")

    def test_notes_blank_allowed(self):
        licence = make_licence(name="No Notes", notes="")
        self.assertEqual(licence.notes, "")

    def test_created_auto_set(self):
        licence = make_licence(name="Auto Created")
        self.assertIsNotNone(licence.created)

    def test_modified_auto_set(self):
        licence = make_licence(name="Auto Modified")
        self.assertIsNotNone(licence.modified)

    def test_ordering_by_name(self):
        make_licence(name="Zebra Licence")
        make_licence(name="Alpha Licence")
        names = list(Licence.objects.values_list("name", flat=True))
        self.assertEqual(names, sorted(names))

    def test_get_absolute_url(self):
        licence = make_licence(name="URL Test")
        expected = reverse("licencing:detail", args=[licence.pk])
        self.assertEqual(licence.get_absolute_url(), expected)


# ===========================================================================
# Licensee model
# ===========================================================================


class LicenseeModelTests(TestCase):
    def test_create_licensee(self):
        licensee = make_licensee()
        self.assertIsNotNone(licensee.pk)

    def test_str(self):
        licensee = make_licensee()
        expected = str(licensee.republisher) + " - " + str(licensee.licence)
        self.assertEqual(str(licensee), expected)

    def test_notes_blank_allowed(self):
        licensee = make_licensee(notes="")
        self.assertEqual(licensee.notes, "")

    def test_unique_constraint(self):
        from django.db import IntegrityError

        republisher = make_republisher()
        licence = make_licence(name="Constrained Licence")
        make_licensee(republisher=republisher, licence=licence)
        with self.assertRaises(IntegrityError):
            make_licensee(republisher=republisher, licence=licence)

    def test_cascade_delete_on_licence(self):
        licensee = make_licensee()
        licence_pk = licensee.licence.pk
        Licence.objects.get(pk=licence_pk).delete()
        self.assertFalse(Licensee.objects.filter(pk=licensee.pk).exists())

    def test_ordering_by_republisher(self):
        # Just verify no error and queryset returns all rows
        make_licensee()
        republisher = Republisher.objects.all()[0]
        make_licensee(
            republisher=republisher,
            licence=make_licence(name="Second Licence"),
        )
        self.assertEqual(Licensee.objects.count(), 2)


# ===========================================================================
# Contract model
# ===========================================================================


class ContractModelTests(TestCase):
    def test_create_minimal_contract(self):
        contract = make_contract()
        self.assertIsNotNone(contract.pk)

    def test_str_contains_licensee(self):
        contract = make_contract()
        self.assertIn(str(contract.licensee), str(contract))

    def test_default_date_from_is_today(self):
        contract = make_contract()
        self.assertEqual(contract.date_from, date.today())

    def test_default_date_to_is_one_year_from_today(self):
        contract = make_contract()
        self.assertEqual(contract.date_to, one_year_from_today())

    def test_notes_blank_allowed(self):
        contract = make_contract(notes="")
        self.assertEqual(contract.notes, "")

    def test_ordering_newest_first(self):
        licensee = make_licensee()
        Contract.objects.create(
            licensee=licensee, date_from=date(2023, 1, 1), date_to=date(2023, 12, 31)
        )
        Contract.objects.create(
            licensee=licensee, date_from=date(2024, 1, 1), date_to=date(2024, 12, 31)
        )
        dates = list(Contract.objects.values_list("date_from", flat=True))
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_unique_constraint(self):
        from django.db import IntegrityError

        licensee = make_licensee()
        d = date(2024, 6, 1)
        Contract.objects.create(licensee=licensee, date_from=d, document="")
        with self.assertRaises(IntegrityError):
            Contract.objects.create(licensee=licensee, date_from=d, document="")

    def test_cascade_delete_on_licensee(self):
        contract = make_contract()
        licensee_pk = contract.licensee.pk
        Licensee.objects.get(pk=licensee_pk).delete()
        self.assertFalse(Contract.objects.filter(pk=contract.pk).exists())


# ===========================================================================
# URL resolution
# ===========================================================================


class UrlTests(TestCase):
    def test_list_url_resolves(self):
        url = reverse("licencing:list")
        self.assertEqual(url, "/licencing/list/")

    def test_detail_url_resolves(self):
        url = reverse("licencing:detail", args=[42])
        self.assertEqual(url, "/licencing/detail/42/")


# ===========================================================================
# Views
# ===========================================================================


class LicenceListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("licencing:list")

    def test_list_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_list_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "licencing/licence_list.html")

    def test_list_shows_all_licences(self):
        make_licence(name="Licence A")
        make_licence(name="Licence B")
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["object_list"]), 2)

    def test_empty_list(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["object_list"]), 0)

    def test_pagination_page_size(self):
        for i in range(105):
            make_licence(name=f"Licence {i:03d}")
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["object_list"]), 100)

    def test_second_page_has_remainder(self):
        for i in range(105):
            make_licence(name=f"Licence {i:03d}")
        response = self.client.get(self.url + "?page=2")
        self.assertEqual(len(response.context["object_list"]), 5)


class LicenceDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.licence = make_licence(name="Detail Licence", text="Detail text")

    def test_detail_returns_200(self):
        response = self.client.get(reverse("licencing:detail", args=[self.licence.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_uses_correct_template(self):
        response = self.client.get(reverse("licencing:detail", args=[self.licence.pk]))
        self.assertTemplateUsed(response, "licencing/licence_detail.html")

    def test_detail_shows_correct_object(self):
        response = self.client.get(reverse("licencing:detail", args=[self.licence.pk]))
        self.assertEqual(response.context["object"], self.licence)

    def test_detail_404_for_missing_pk(self):
        response = self.client.get(reverse("licencing:detail", args=[99999]))
        self.assertEqual(response.status_code, 404)
