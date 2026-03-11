from django.db import models
from django.urls import reverse
from filebrowser.fields import FileBrowseField
from datetime import date
from dateutil.relativedelta import relativedelta


class Licence(models.Model):
    name = models.CharField(max_length=200, unique=True)
    text = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = [
            "name",
        ]

    def get_absolute_url(self):
        return reverse(
            "licencing:detail",
            args=[
                self.pk,
            ],
        )


class Licensee(models.Model):
    republisher = models.ForeignKey("republisher.Republisher", on_delete=models.CASCADE)
    licence = models.ForeignKey(Licence, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return str(self.republisher) + " - " + str(self.licence)

    class Meta:
        ordering = [
            "republisher",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "republisher",
                    "licence",
                ],
                name="unique_licensee",
            ),
        ]


def one_year_from_today():
    return date.today() + relativedelta(years=1) - relativedelta(days=1)


class Contract(models.Model):
    licensee = models.ForeignKey(Licensee, on_delete=models.CASCADE)
    document = FileBrowseField(max_length=200, directory="images/", blank=True)
    notes = models.TextField(blank=True)
    date_from = models.DateField(default=date.today)
    date_to = models.DateField(default=one_year_from_today)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return " ".join([str(self.licensee), str(self.document), str(self.date_from)])

    class Meta:
        ordering = [
            "-date_from",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "licensee",
                    "document",
                    "date_from",
                ],
                name="unique_contract",
            ),
        ]
