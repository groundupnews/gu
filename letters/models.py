from django.db import models
from django.utils import timezone
from django.urls import reverse
from newsroom.models import Article

# Create your models here.


class LetterQuerySet(models.QuerySet):

    def published(self):
        return self.filter(published__lte=timezone.now())

    def processed(self):
        pks = [letter.pk for letter in Letter.objects.all()
               if letter.is_processed()]
        return self.filter(pk__in=pks)

    def unprocessed(self):
        pks = [letter.pk for letter in Letter.objects.all()
               if letter.is_unprocessed()]
        return self.filter(pk__in=pks)


class Letter(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    byline = models.CharField(max_length=200)
    email = models.EmailField()
    title = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    rejected = models.BooleanField(default=False)
    note_to_writer = models.TextField(blank=True)
    notified_letter_writer = models.BooleanField(default=False)
    notified_editors = models.BooleanField(default=False)
    replace_with_note = models.BooleanField(default=False,
                                            help_text="If checked, then "
                                            "the note to the writer "
                                            "completely overrides the "
                                            "standard response sent "
                                            "to writer.")
    notes_for_editors = models.TextField(blank=True)
    being_dealt_with = models.BooleanField(default=False)
    css_classes = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    published = models.DateTimeField(blank=True, null=True,
                                     verbose_name='publish time')
    position = models.IntegerField(default=0)

    objects = LetterQuerySet.as_manager()

    def is_published(self):
        return (self.rejected is False and self.published is not None) and \
            (self.published <= timezone.now())

    is_published.boolean = True
    is_published.short_description = 'published'

    def is_processed(self):
        return (self.rejected is True) or (self.published is not None)

    is_processed.boolean = True
    is_processed.short_description = 'processed'

    def is_unprocessed(self):
        return not self.is_processed()

    is_unprocessed.boolean = True
    is_unprocessed.short_description = 'processed'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('newsroom:article.detail', args=[self.article.slug, ]) + \
            "#letter-" + str(self.pk)

    class Meta:
        verbose_name = "letter"
        verbose_name_plural = "letters to the editor"

        ordering = ['article', 'position', 'published', ]
