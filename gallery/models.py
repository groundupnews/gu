from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import random


from filebrowser.fields import FileBrowseField
from newsroom.models import Author

from . import settings

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

    def get_random_photo(self):
        photographs = self.photograph_set.all()
        i = random.randint(0, len(photographs) - 1)
        return photographs[i]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('album.detail', args=[self.pk, ])

    class Meta:
        ordering = ['name', ]


class Photograph(models.Model):
    image = FileBrowseField(max_length=200, directory=settings.DIRECTORY)
    albums = models.ManyToManyField(Album, blank=True)
    photographer =  models.ForeignKey(Author, blank=True, null=True)
    suggested_caption = models.CharField(max_length=600, blank=True)
    alt = models.CharField(max_length=600, blank=True, help_text=
                           "Description of image for assistive technology")
    date_taken = models.DateField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    copyright = models.TextField(blank=True, help_text="Leave blank for default")
    credit = models.TextField(blank=True, help_text="Leave blank for default")
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    keywords = models.ManyToManyField(Keyword, blank=True)

    def __str__(self):
        return ", ".join([str(self.image).rsplit('/',1)[-1],
                          str(self.photographer),])

    class Meta:
        ordering = ['-modified', ]

    def get_absolute_url(self):
        return reverse('photo.detail', args=[self.pk, ])

    def thumbnail(self):
        return format_html(
            '<img src="/media/{}" alt="{}">',
            str(self.image.version_generate("thumbnail")),
            self.suggested_caption
        )
