from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from newsroom.models import Article

# Create your models here.


class LetterQuerySet(models.QuerySet):

    def published(self):
        return self.filter(published__lte=timezone.now())


class Letter(models.Model):
    article = models.ForeignKey(Article)
    byline = models.CharField(max_length=200)
    email = models.EmailField()
    title = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    rejected = models.BooleanField(default=False)
    note_to_writer = models.TextField(blank=True)
    notified_letter_writer = models.BooleanField(default=False)
    notified_editors = models.BooleanField(default=False)
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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article.detail', args=[self.article.slug, ]) + \
            "#letter-" + str(self.pk)

    class Meta:
        verbose_name = "letter"
        verbose_name_plural = "letters to the editor"

        ordering = ['article', 'position', 'published', ]
