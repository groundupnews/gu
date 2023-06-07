import datetime
from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware
from django.urls import reverse
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

import re

EVENT_CHOICES = (
        ("R", "Judgment reserved", ),
        ("H", "Judgment handed down", ),
        ("I", "Judge died or incapacitated", ),
        ("S", "Case settled", ),
        ("O", "Other", ),
        )

PROCESS_CHOICES = (
        ("U", "Unprocessed", ),
        ("I", "Ignore", ),
        ("P", "Processed", )
        )

COURTS = [
        "Competition Appeal Court",
        "Competition Tribunal",
        "Companies Tribunal",
        "Consumer Affairs Court",
        "Consumer Goods and Services Ombud",
        "Constitutional Court",
        "Court of the Commissioner of Patents",
        "Commercial Crime Court",
        "Eastern Cape High Court, Bhisho",
        "Eastern Cape High Court, Grahamstown",
        "Eastern Cape High Court, Gqeberha",
        "Eastern Cape High Court, Makhanda",
        "Eastern Cape High Court, Mthatha",
        "Eastern Cape High Court, East London local Court",
        "Eastern Cape High Court, Port Elizabeth",
        "Electoral Court",
        "Equality Court",
        "Financial Service Tribunal",
        "Free State High Court, Bloemfontein",
        "Kwazulu-Natal High Court, Durban",
        "Kwazulu-Natal High Court, Pietermaritzburg",
        "Industrial Court",
        "Labour Appeal Court",
        "Labour Court Cape Town",
        "Labour Court Johannesburg",
        "Labour Court Port Elizabeth",
        "Labour Court Polokwane",
        "Labour Court Durban",
        "Land Claims Court",
        "Law Reform Commission",
        "Limpopo High Court",
        "Limpopo High Court, Polokwane",
        "Limpopo High Court, Thohoyandou",
        "Mbombela High Court, Mpumalanga",
        "Middelburg High Court, Mpumalanga",
        "National Consumer Tribunal",
        "Northern Cape High Court, Kimberley",
        "North Gauteng High Court, Pretoria",
        "North West High Court, Mafikeng",
        "South Gauteng High Court, Johannesburg",
        "Special Tribunal",
        "Supreme Court of Appeal",
        "Tax Court",
        "Water Tribunal",
        "Western Cape High Court, Cape Town",
        ]


def validate_case(value):
    pattern = '^\s*\w*\s*\d+/\d+\s*$'
    if not re.match(pattern, value):
        raise ValidationError("%(value)s is not a valid case number.",
                              params={"value": value},
        )


class Court(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name', ]


class Event(models.Model):
    case_id = models.CharField(
            max_length=20,
            validators=[validate_case],
            help_text="Enter a valid South African court case id.")
    case_name = models.CharField(
            max_length=200, blank=True,
            help_text="E.g. Jane Doe and Others v Joe Bloggs and Other")
    accept_case_name = models.BooleanField(default=False)
    court = models.ForeignKey(Court, on_delete=models.CASCADE,
            null=True, blank=True,
            help_text="Select the court where this case was heard.")
    accept_court = models.BooleanField(default=False)
    judges = models.TextField(blank=True,
            max_length=1000,
            verbose_name="Judge(s)",
            help_text="Enter first and surnames of judges, one per line. "
            "Please enter at least one judge.")
    accept_judges = models.BooleanField(default=False)
    event_type = models.CharField(
            max_length=3, verbose_name="What happened",
            help_text="Indicate if judgment was reserved, handed down or "
            "something else happened.",
            choices=EVENT_CHOICES)
    accept_event_type = models.BooleanField(default=False)
    event_date = models.DateField(
            null=True, blank=True,
            verbose_name="Date it happened",
            help_text="Please give the exact date. "
            "If you're not certain, please indicate in the notes "
            "below.")
    accept_event_date = models.BooleanField(default=False)
    document_url = models.URLField(
            blank=True,
            help_text="URL of document that may assist verification.")
    accept_document_url = models.BooleanField(default=False)
    document = models.FileField(null=True, blank=True,
            help_text="Document that may assist verification (maximum 10MB)")
    notes = models.TextField(blank=True, max_length=2000,
            help_text="Use this to provide further information")
    accept_notes = models.BooleanField(default=False)
    email_address = models.EmailField(
            verbose_name='Your email address',
            help_text="We may need to contact you but we will not share "
            "your email address with anyone else.")
    process_status = models.CharField(max_length=2, choices=PROCESS_CHOICES,
            default="U")
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.case_id + '-' + str(self.pk) + \
                ' (' + self.case_name + ')'

    def get_absolute_url(self):
        return reverse('judgment:case.detail', args=[self.pk, ])


    @staticmethod
    def get_consolidated_cases(case_ids=None, reserved=None,
                               months=None):
        query = Q(process_status='P')

        if case_ids:
            query = query & Q(case_id__in=case_ids)
        cases = Event.objects.filter(query).order_by(
                'case_id', 'event_date')
        consolidated = []
        current = None
        for c in cases:
            if c.case_id != current:
                consolidated.append({
                    'case_id': c.case_id,
                    'case_name': "",
                    'court': "",
                    'court_pk': "",
                    'judges': "",
                    'status': "",
                    'status_display': "",
                    'date_reserved': "",
                    'date_current': "",
                    'notes': ""
                    })
                current = c.case_id
            record = consolidated[-1]
            if c.accept_case_name:
                record['case_name'] = c.case_name
            if c.accept_court:
                record['court'] = str(c.court)
                record['court_pk'] = str(c.court.pk)
            if c.accept_judges:
                record['judges'] = c.judges
            if c.accept_event_type:
                record['status'] = c.event_type
                record['status_display'] = c.get_event_type_display()
            if c.accept_event_date:
                record['date_current'] = datetime.datetime(
                        c.event_date.year, c.event_date.month, c.event_date.day)
                record['event_date'] = record['date_current']
                if c.event_type == 'R':
                    record['date_reserved'] = datetime.datetime(
                        c.event_date.year, c.event_date.month, c.event_date.day)
            if c.accept_notes:
                record['notes'] = c.notes
        if reserved is True:
            consolidated = [c for c in consolidated
                    if c['status'] == 'R']
        elif reserved is False:
            consolidated = [c for c in consolidated
                    if c['status'] != 'R']
        if months:
            delta = relativedelta(months=months)
            cutoff = datetime.datetime.now() - delta
            consolidated = [c for c in consolidated if c['date_current'] and
                     cutoff > c['date_current']]
        return consolidated

    class Meta:
        ordering = ['case_id', '-modified',]

