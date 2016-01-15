from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags

import tagulous
from filebrowser.fields import FileBrowseField
from filebrowser.settings import VERSIONS

from . import settings

from .utils import visible_text_in_html

import logging

logger = logging.getLogger("django")

class Author(models.Model):
    first_names = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200)
    title = models.CharField(max_length=20, blank=True)
    photo = FileBrowseField(max_length=200, directory="images/",
                            blank=True, null=True, )
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=200, blank=True)
    facebook = models.CharField(max_length=200, blank=True)
    googleplus = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    email_is_private = models.BooleanField(default=True)
    telephone = models.CharField(max_length=200, blank=True)
    cell = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "first_names__icontains", "last_name__icontains",)

    def __str__(self):
        return " ".join([self.title,self.first_names, self.last_name]).strip()

    def get_absolute_url(self):
        return reverse('author.detail', args=[self.pk,])

    class Meta:
        ordering = ["last_name","first_names",]


class Region(tagulous.models.TagTreeModel):
    def get_absolute_url(self):
        return reverse('region.detail', args=[self.path,])

    class TagMeta:
        case_sensitive = False

class Topic(tagulous.models.TagModel):
    introduction = models.TextField(blank=True,
                                    help_text="Use unfiltered HTML. "
                                    "If this is not blank, "
                                    "the default template does not render any "
                                    "other fields before the article list.")
    icon = FileBrowseField("Image", max_length=200, directory="images/",
                                    blank=True, null=True)
    template = models.CharField(max_length=200,
                                default="newsroom/topic_detail.html")

    def get_absolute_url(self):
        return reverse('topic.detail', args=[self.slug,])

    class TagMeta:
        case_sensitive = False
        max_count=8
        space_delimiter=False

class Category(tagulous.models.TagModel):
    def get_absolute_url(self):
        return reverse('category.detail', args=[self.slug,])

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    class TagMeta:
        case_sensitive = False
        space_delimiter = False
        initial="Brief, News, " \
            "Feature, Photo Essay, " \
            "Analysis, Opinion, Photo"


# Used to select sizes of images
IMAGE_SIZE_CHOICES = [(item,item,) for item in VERSIONS]
IMAGE_SIZE_CHOICES.append(('LEAVE', 'LEAVE',))

# Used to prevent disaster on the template fields
DETAIL_TEMPLATE_CHOICES = (
    ("newsroom/article_detail.html", "Standard"),
)

SUMMARY_TEMPLATE_CHOICES = (
    ("newsroom/article_summary.html", "Standard"),
    ("newsroom/photo_summary.html", "Great Photo"),
    ("newsroom/text_summary.html", "Text only"),
)


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published__lte=timezone.now())
    def list_view(self):
        return self.published().filter(exclude_from_list_views=False)

class Article(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    summary_image = FileBrowseField("Image", max_length=200, directory="images/",
                                    blank=True, null=True)
    summary_image_size = models.CharField(
        choices=IMAGE_SIZE_CHOICES,
        default=settings.ARTICLE_SUMMARY_IMAGE_SIZE,
        max_length=20,
        help_text="Choose 'LEAVE' if image size should not be changed.")
    summary_text = models.TextField(blank=True)
    author_01 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_01",
                                  verbose_name="first author")
    author_02 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_02",
                                  verbose_name="second author")
    author_03 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_03",
                                  verbose_name="third author")
    author_04 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_04",
                                  verbose_name="fourth author")
    author_05 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_05",
                                  verbose_name="fifth author")
    byline = models.CharField(max_length=200, blank=True,
                              verbose_name='customised byline',
                              help_text="If this is not blank it "
                              "overrides the value of the author fields")
    primary_image = FileBrowseField(max_length=200, directory="images/",
                                   blank=True, null=True)
    primary_image_size = models.CharField(
        choices=IMAGE_SIZE_CHOICES,
        default=settings.ARTICLE_PRIMARY_IMAGE_SIZE,
        max_length=20,
        help_text="Choose 'LEAVE' if image size should not be changed.")
    external_primary_image = models.URLField(blank=True, max_length=500,
            help_text="If the primary image has a value, it overrides this.")
    primary_image_caption = models.CharField(max_length=600, blank=True)
    body = models.TextField(blank=True)
    published = models.DateTimeField(blank=True, null=True,
                                     verbose_name='publish time')
    category = tagulous.models.SingleTagField(
        to=Category,
        default=4 # News
    )
    region = tagulous.models.SingleTagField(to=Region, blank=True)
    topics = tagulous.models.TagField(
        to=Topic,
        blank=True
    )
    copyright = models.TextField(blank=True, default=settings.ARTICLE_COPYRIGHT)
    template = models.CharField(max_length=200,
                                choices=DETAIL_TEMPLATE_CHOICES,
                                default="newsroom/article_detail.html")
    summary_template = models.CharField(max_length=200,
                                        choices=SUMMARY_TEMPLATE_CHOICES,
                                        default="newsroom/article_summary.html")
    include_in_rss = models.BooleanField(default=True)
    comments_on = models.BooleanField(default=True)
    exclude_from_list_views = models.BooleanField(default=False)
    # Neccessary for importing old Drupal articles
    disqus_id = models.CharField(blank=True, max_length=20)

    stickiness = models.IntegerField(
        default=0,
        help_text="The higher the value, the stickier the article.")
    slug = models.SlugField(max_length=200, unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    # Cached fields
    cached_byline = models.CharField(max_length=500, blank=True)
    cached_byline_no_links = models.CharField(max_length=400, blank=True,
                                     verbose_name="Byline")
    cached_primary_image = models.URLField(blank=True, max_length=500)
    cached_summary_image = models.URLField(blank=True, max_length=500)
    cached_summary_text = models.TextField(blank=True)
    cached_summary_text_no_html = models.TextField(blank=True)

    objects = ArticleQuerySet.as_manager()

    def is_published(self):
        return (self.published is not None) and \
            (self.published <= timezone.now())

    is_published.boolean = True
    is_published.short_description = 'published'

    # Methods that calculate cache fields

    '''Used to generate the cached byline upon model save, so
    there's less processing for website user requests.
    '''
    def calc_byline(self, links=False):
        if self.byline:
            return self.byline
        else:
            names = [self.author_01, self.author_02, \
                     self.author_03, self.author_04, \
                     self.author_05
            ]
            if links:
                names = [ "<a href='" + name.get_absolute_url() + \
                          "'>" + str(name) + "</a>" \
                          for name in names if name != None]
            else:
                names = [ str(name) for name in names if name != None]
        if len(names) == 0:
            return ""
        elif len(names) == 1:
            return "By " + names[0]
        elif len(names) == 2:
            return "By " + names[0] + " and " + names[1]
        else:
            names[-1] = " and " + names[-1]
            names_middle = [", " + name for name in names[1:-1]]
            names_string = names[0] + "".join(names_middle) + names[-1]
            return "By " + names_string

    '''Used to generate the cached primary image upon model save, so
    there's less processing for website user requests.
    '''
    def calc_primary_image(self):
        if self.primary_image:
            if self.primary_image_size == "LEAVE":
                return self.primary_image.url
            else:
                return self.primary_image.version_generate(
                    self.primary_image_size).url
        return self.external_primary_image


    '''Used to generate the cached summary image upon model save, so
    there's less processing for website user requests.
    '''
    def calc_summary_image(self):
        image_size = self.summary_image_size
        if self.summary_image:
            if self.summary_image_size == 'LEAVE':
                return self.summary_image.url
            else:
                return self.summary_image.version_generate(image_size).url

        if self.primary_image:
            if self.summary_image_size == 'LEAVE':
                return self.primary_image.url
            else:
                return self.primary_image.version_generate(image_size).url

        if self.external_primary_image:
            return self.external_primary_image

        return ""


    '''Used to generate the cached summary text upon model save, so
    there's less processing for website user requests.
    '''
    def calc_summary_text(self):
        if self.summary_text:
            return self.summary_text
        if self.subtitle:
            return self.subtitle

        # Not very robust, but using BeautifulSoup was too slow
        # and the server would time out.
        start_para = str(self.body).partition("<p")

        if start_para[2] == None:
            return ""
        start_para = start_para[2].partition(">")

        if start_para[2] == None:
            return ""
        end_para = start_para[2].partition("</p>")

        if end_para[1] == None or end_para[0] == None:
            return ""
        return strip_tags(end_para[0])


    '''Legacy code from when more complex processing was done. But too
    time-consuming and server times out.
    '''
    def calc_summary_text_no_html(self):
        return strip_tags(self.cached_summary_text)

    def save(self, *args, **kwargs):
        self.cached_byline = self.calc_byline(True)
        self.cached_byline_no_links = self.calc_byline(False)
        try:
             self.cached_primary_image = self.calc_primary_image()
        except:
             self.cached_primary_image = ""
        try:
             self.cached_summary_text = self.calc_summary_text()
        except:
             self.cached_summary_text = ""
        try:
             self.cached_summary_text_no_html = self.calc_summary_text_no_html()
        except:
             self.cached_summary_text_no_html = ""
        try:
             self.cached_summary_image = self.calc_summary_image()
        except:
             self.cached_summary_image = ""
        super(Article, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('article.detail', args=[self.slug,])


    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-stickiness", "-published",]
