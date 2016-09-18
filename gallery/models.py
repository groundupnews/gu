from django.db import models

from . import settings.
from newsroom.models import Author

class Keyword(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def get_absolute_url(self):
        return reverse('keyword.detail', args=[self.slug, ])

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    class Meta:
        ordering = ['name', ]

class Album(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

class Photo(models.Model):
    image = FileBrowseField(max_length=200, directory=GALLERY_FOLDER)
    photographer =  models.ForeignKey(Author, blank=True, null=True)
    suggested_caption = models.CharField(max_length=600, blank=True)
    date_taken = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    keywords = models.ManyToManyField(Keyword, blank=True)
