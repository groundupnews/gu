from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import format_html
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
        num_photos = len(photographs)
        if num_photos:
            i = random.randint(0, num_photos - 1)
            return photographs[i]
        else:
            return None

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('album.detail', args=[self.pk, ])

    @staticmethod
    def autocomplete_search_fields():
        return ("pk__iexact", "name__icontains")

    class Meta:
        ordering = ['name', ]


class PhotographQuerySet(models.QuerySet):

    def ordered_by_date_taken(self):
        return self.order_by("-date_taken")


class Photograph(models.Model):
    image = FileBrowseField(max_length=200, directory=settings.DIRECTORY)
    albums = models.ManyToManyField(Album, blank=True)
    photographer = models.ForeignKey(Author, blank=True, null=True)
    suggested_caption = models.CharField(max_length=600, blank=True)
    alt = models.CharField(max_length=600, blank=True,
                           verbose_name="short title",
                           help_text="Description of image "
                           "for assistive technology")
    date_taken = models.DateField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    copyright = models.TextField(blank=True,
                                 help_text="Leave blank for default")
    credit = models.TextField(blank=True, help_text="Leave blank for default")
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    keywords = models.ManyToManyField(Keyword, blank=True)

    objects = PhotographQuerySet.as_manager()

    def __str__(self):
        return ", ".join([str(self.image).rsplit('/', 1)[-1],
                          str(self.photographer), ])

    def get_absolute_url(self):
        return reverse('photo.detail', args=[self.pk, ])

    def thumbnail(self):
        return format_html(
            '<img src="/media/{}" alt="{}">',
            str(self.image.version_generate("thumbnail")),
            self.suggested_caption
        )

    # def save(self, *args, **kwargs):
    #     super(Photograph, self).save(*args, **kwargs)
    #     print("Pk:", self.pk)
    #     print("Albums:", self.albums)
    #     print("Duplicates:", self.duplicate_set.all())
    #     for duplicate in self.duplicate_set.all():
    #         duplicate.create_duplicate()

    class Meta:
        ordering = ['-featured', '-modified', ]


"""Hack class to make it easy to upload multiple photos into database,
without having to write a fancy widget to do it.
"""


class Duplicate(models.Model):
    photograph = models.ForeignKey(Photograph)
    image = FileBrowseField(max_length=200, directory=settings.DIRECTORY)
    processed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    # def create_duplicate(self):
    def save(self, *args, **kwargs):
        if self.processed is False:
            p = Photograph()
            p.image = self.image
            p.photographer = self.photograph.photographer
            p.suggested_caption = self.photograph.suggested_caption
            p.alt = self.photograph.alt
            p.date_taken = self.photograph.date_taken
            p.credit = self.photograph.credit
            p.save()
            p.keywords.add(*self.photograph.keywords.all())
            p.albums.add(*self.photograph.albums.all())
            p.save()
            self.processed = True
            super(Duplicate, self).save(*args, **kwargs)

    class Meta:
        unique_together = ("photograph", "image", )
