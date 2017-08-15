from django.db import models
from newsroom.models import Article
from socialmedia.common import SCHEDULE_RESULTS
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def validate_email_list(email_string_list):
    email_list = email_string_list.split(",")
    for email in email_list:
        try:
            validate_email(email.strip())
        except ValidationError:
            raise ValidationError("Email address is invalid: {}".format(email))


class Republisher(models.Model):
    name = models.CharField(max_length=200, unique=True)
    email_addresses = models.CharField(max_length=250,
                                       validators=[validate_email_list, ])
    message = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name", ]


class RepublisherArticle(models.Model):
    article = models.ForeignKey(Article)
    republisher = models.ForeignKey(Republisher)
    wait_time = models.PositiveIntegerField(
        default=0,
        help_text="Minimum number of minutes after publication till sent.")
    note = models.TextField(blank=True,
                            help_text="A note for the republisher "
                            "specific to this article.")
    status = models.CharField(max_length=20,
                              choices=SCHEDULE_RESULTS,
                              default="scheduled")

    def __str__(self):
        return str(self.article) + " - " + str(self.republisher)

    def published(self):
        return self.article.published

    published.admin_order_field = 'article__published'

    class Meta:
        ordering = ["article__published", "republisher", ]
        unique_together = (("article", "republisher"),)
