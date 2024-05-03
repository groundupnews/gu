from django.db import models
from django.utils import timezone
from django.urls import reverse

PROCESS_CHOICES = (
    ("O", "Old"),
    ("U", "Unprocessed"),
    ("Q", "Query"),
    ("I", "Ignore"),
    ("R", "Notify reader only"),
    ("P", "Publish only"),
    ("B", "Publish and notify reader"),
)


class QandAQuerySet(models.QuerySet):

    def published(self):
        return self.filter(published__lte=timezone.now())

class QandA(models.Model):
    summary_question = models.CharField(max_length=200)
    full_question = models.TextField(blank=True)
    summary_answer = models.CharField(max_length=200, blank=True)
    full_answer = models.TextField(blank=True)
    original_question = models.TextField(blank=True)
    answer_for_sender = models.TextField(blank=True)
    sender_name = models.CharField(max_length=200, blank=True)
    sender_email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    notify_sender = models.BooleanField(default=False)
    sender_notified = models.BooleanField(default=False)
    status = models.CharField(max_length=2, default="U",
                              choices=PROCESS_CHOICES)
    published = models.DateTimeField(blank=True, null=True)
    recommended = models.BooleanField(default=True)
    salutation = models.CharField(max_length=200, blank=True,
                                  verbose_name="Agony aunt", default="")
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    topics = models.ManyToManyField('newsroom.Topic',
                                    blank=True)

    objects = QandAQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('agony:detail', args=[self.pk, ])

    def __str__(self):
        return self.summary_question

    def is_published(self):
        return (self.published is not None) and \
            (self.published <= timezone.now())

    def save(self, *args, **kwargs):
        if self.status == 'R': # Notify reader
            self.notify_sender = True
            self.published = None
        elif self.status == 'P': # Publish only
            self.published = timezone.now()
            self.notify_sender  = False
        elif self.status == 'B':
            self.notify_sender = True
            self.published = timezone.now()
        elif self.status == 'I':
            self.notify_sender  = False
            self.published = None
        super(QandA, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-published',]
        verbose_name = 'Question and Answer'
        verbose_name_plural = 'Questions and Answers'
