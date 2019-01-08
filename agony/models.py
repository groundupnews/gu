from django.db import models
from django.utils import timezone
from django.urls import reverse
from newsroom.models import Topic

# Create your models here.

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
    published = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    topics = models.ManyToManyField(Topic, blank=True)

    objects = QandAQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('agony:detail', args=[self.pk, ])

    def __str__(self):
        return self.summary_question

    def is_published(self):
        return (self.published is not None) and \
            (self.published <= timezone.now())

    class Meta:
        ordering = ['-published',]
        verbose_name = 'Question and Answer'
        verbose_name_plural = 'Questions and Answers'
