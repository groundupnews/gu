import datetime
import logging
import traceback
from urllib.parse import urlparse

import smartypants
from allauth.account.signals import password_changed
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db import models
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from filebrowser.fields import FileBrowseField
from socialmedia.common import SCHEDULE_RESULTS

from . import settings, utils

logger = logging.getLogger("django")


OVERRIDE_COMMISSION_CHOICES = (
    ("NO", "No"),
    ("PROCESS", "Process commissions for this article"),
    ("NOPROCESS", "Don't process commissions for this article"),
)


BYLINE_CHOICES = (
    ("ST", "Standard"),
    ("TP", "Text By [First Author] Photos By [Second Author]"),
)


class Author(models.Model):
    first_names = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200)
    freelancer = models.BooleanField(default=False)
    email = models.EmailField(blank=True)
    title = models.CharField(max_length=20, blank=True)
    telephone = models.CharField(max_length=200, blank=True)
    cell = models.CharField(max_length=200, blank=True)

    # Fields that contain default values for invoices
    identification = models.CharField(max_length=20, blank=True,
                                      help_text="SA ID, passport or some form "
                                      "of official identification")
    dob = models.DateField(blank=True, null=True, verbose_name="date of birth",
                           help_text="Please fill this in. Required by SARS.")
    address = models.TextField(blank=True,
                               help_text="Please fill this in. "
                               "Required by SARS.")
    bank_name = models.CharField(max_length=20, blank=True)
    bank_account_number = models.CharField(max_length=20, blank=True)
    bank_account_type = models.CharField(max_length=20, default="CURRENT")
    bank_branch_name = models.CharField(max_length=20, blank=True,
                                        help_text="Unnecessary for Capitec, "
                                        "FNB, Standard, Nedbank and Absa")
    bank_branch_code = models.CharField(max_length=20, blank=True,
                                        help_text="Unnecessary for Capitec, "
                                        "FNB, Standard, Nedbank and Absa")
    swift_code = models.CharField(max_length=12, blank=True,
                                  help_text="Only relevant for "
                                  "banks outside SA")
    iban = models.CharField(max_length=34, blank=True,
                            help_text="Only relevant "
                            "for banks outside SA")
    tax_no = models.CharField(max_length=50, blank=True,
                              help_text="Necessary for SARS.")
    tax_percent = models.DecimalField(max_digits=2, decimal_places=0,
                                      default=25, verbose_name="tax %",
                                      help_text="Unless you have a tax "
                                      "directive we have to deduct 25% "
                                      "PAYE for SARS.")
    vat = models.DecimalField(max_digits=2, decimal_places=0, default=0,
                              verbose_name="vat %",
                              help_text="If you are VAT regisered "
                              "set this to 14 else leave at 0")

    ####
    email_is_private = models.BooleanField(default=True)
    photo = FileBrowseField(max_length=200, directory="images/", blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=200, blank=True)
    facebook = models.CharField(max_length=200, blank=True)
    googleplus = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, null=True, blank=True,
                                on_delete=models.CASCADE)
    password_changed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "first_names__icontains",
                "last_name__icontains",)

    def __str__(self):
        return " ".join([self.title, self.first_names,
                         self.last_name]).strip()


    def get_absolute_url(self):
        return reverse('newsroom:author.detail', args=[self.pk, ])

    def save(self, *args, **kwargs):
        if self.pk is None or self.user is None:
            pwd = None
            site = Site.objects.get_current()
            if self.user is None:
                pwd = utils.generate_pwd()
                username = (self.first_names +
                            self.last_name).replace(" ", "_")
                user = User.objects.create_user(username=username,
                                                first_name=self.first_names,
                                                last_name=self.last_name,
                                                email=self.email,
                                                password=pwd)
                user.save()
                self.user = user
                super(Author, self).save(*args, **kwargs)
            subject = "Account created for you on GroundUp"
            message = render_to_string(
                'account/email/account_created_message.txt',
                {'user': user,
                 'author': self,
                 'pwd': pwd,
                 'site': site})
            try:
                send_mail(subject,
                          message,
                          settings.EDITOR,
                          [self.email, settings.EDITOR, ])
            except Exception as e:
                log_message = "Error author creation email failed: " + \
                              self.email + "\n" + traceback.print_exc() + \
                              "\n" + str(e)
                logger.error(log_message)
        else:
            # Design error for legacy reasons: email is duplicated in Author
            # And User
            if self.user is not None:
                self.user.email = self.email
                self.user.save()
            super(Author, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('first_names', 'last_name'), )
        ordering = ["last_name", "first_names", ]


class Region(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def get_descendants(self):
        regions = Region.objects.filter(name__startswith=(self.name + "/"))
        return regions

    def get_absolute_url(self):
        return reverse('newsroom:region.detail', args=[self.name, ])

    def get_specific(self):
        index = self.name.rfind("/")
        if index >= 0 and index < len(self.name):
            return self.name[index + 1:]
        else:
            return self.name

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    class Meta:
        ordering = ['name', ]


class Topic(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    introduction = models.TextField(blank=True,
                                    help_text="Use unfiltered HTML. "
                                    "If this is not blank, "
                                    "the default template does not render any "
                                    "other fields before the article list.")
    icon = FileBrowseField("Image", max_length=200, directory="images/",
                           blank=True)
    template = models.CharField(max_length=200,
                                default="newsroom/topic_detail.html")
    newest_first = models.BooleanField(default=True)

    def count_articles(self):
        return Article.objects.filter(topics=self).count()

    def get_absolute_url(self):
        return reverse('newsroom:topic.detail', args=[self.slug, ])

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    class Meta:
        ordering = ['name', ]


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    def get_absolute_url(self):
        return reverse('newsroom:category.detail', args=[self.slug, ])

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        ordering = ['name', ]


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


# def latest_article(request):
#    return Entry.objects.published().latest("modified").modified

class Article(models.Model):
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=250, blank=True)
    summary_image = FileBrowseField("Image", max_length=200,
                                    directory="images/",
                                    blank=True)
    summary_image_size = models.CharField(
        default=settings.ARTICLE_SUMMARY_IMAGE_SIZE,
        max_length=20,
        help_text="Choose 'LEAVE' if image size should not be changed.")
    summary_image_alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="Description of image for assistive technology.")
    summary_text = models.TextField(blank=True)
    author_01 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_01",
                                  verbose_name="first author",
                                  on_delete=models.CASCADE)
    author_02 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_02",
                                  verbose_name="second author",
                                  on_delete=models.CASCADE)
    author_03 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_03",
                                  verbose_name="third author",
                                  on_delete=models.CASCADE)
    author_04 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_04",
                                  verbose_name="fourth author",
                                  on_delete=models.CASCADE)
    author_05 = models.ForeignKey(Author, blank=True, null=True,
                                  related_name="author_05",
                                  verbose_name="fifth author",
                                  on_delete=models.CASCADE)
    byline = models.CharField(max_length=200, blank=True,
                              verbose_name='customised byline',
                              help_text="If this is not blank it "
                              "overrides the value of the author fields")
    byline_style = models.CharField(max_length=2, choices=BYLINE_CHOICES,
                                    default="ST")
    primary_image = FileBrowseField(max_length=200, directory="images/",
                                    blank=True)
    primary_image_size = models.CharField(
        default=settings.ARTICLE_PRIMARY_IMAGE_SIZE,
        max_length=20,
        help_text="Choose 'LEAVE' if image size should not be changed.")
    primary_image_alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="Description of image for assistive technology.")
    external_primary_image = models.CharField(blank=True,
                                              verbose_name="alternative URL",
                                              max_length=500,
                                              help_text="Use this instead "
                                              "of primary. But note that "
                                              "if primary image has a value, "
                                              "it overrides this.")
    primary_image_caption = models.CharField(max_length=600, blank=True)
    body = models.TextField(blank=True)
    use_editor = models.BooleanField(default=True)
    published = models.DateTimeField(blank=True, null=True,
                                     verbose_name='publish time')
    recommended = models.BooleanField(default=True)
    category = models.ForeignKey(Category, default=4,
                                 on_delete=models.CASCADE)
    region = models.ForeignKey(Region, blank=True, null=True,
                               on_delete=models.CASCADE)
    topics = models.ManyToManyField(Topic, blank=True)
    main_topic = models.ForeignKey(Topic, blank=True,
                                   on_delete=models.CASCADE,
                                   null=True,
                                   related_name="main",
                                   help_text="Used for generating"
                                   "'See also' list of articles.")
    copyright = models.TextField(blank=True,
                                 default=settings.ARTICLE_COPYRIGHT)
    template = models.CharField(max_length=200,
                                choices=DETAIL_TEMPLATE_CHOICES,
                                default="newsroom/article_detail.html")
    summary_template = models.CharField(
        max_length=200,
        choices=SUMMARY_TEMPLATE_CHOICES,
        default="newsroom/article_summary.html")
    include_in_rss = models.BooleanField(default=True)
    letters_on = models.BooleanField(default=True)
    comments_on = models.BooleanField(default=False)
    collapse_comments = models.BooleanField(default=True)
    exclude_from_list_views = models.BooleanField(default=False)
    suppress_ads = models.BooleanField(default=False,
                                       help_text="Only suppresses ads "
                                       "that are external to article. "
                                       "You can still create ads in article.")
    promote_article = models.BooleanField(default=True)
    encourage_republish = models.BooleanField(default=True)
    activate_slideshow = models.BooleanField(default=False)
    additional_head_scripts = models.TextField(blank=True)
    additional_body_scripts = \
        models.TextField(blank=True,
                         help_text="Include things like additional javascript "
                         "that should come at bottom of article")
    undistracted_layout = models.BooleanField(default=False)
    # Neccessary for importing old Drupal articles
    disqus_id = models.CharField(blank=True, max_length=20)

    stickiness = models.IntegerField(
        default=0,
        help_text="The higher the value, the stickier the article.")
    slug = models.SlugField(max_length=200, unique=True)

    # Facebook
    facebook_wait_time = models.PositiveIntegerField(
        default=0,
        help_text="Minimum number of minutes "
        "after publication "
        "till post.")
    facebook_image = FileBrowseField(
        max_length=200, directory="images/", blank=True,
        verbose_name="image", help_text="Leave blank to use primary image.")
    facebook_image_caption = models.CharField(
        max_length=200, verbose_name="caption",
        help_text="Leave blank to use primary "
        "image caption.", blank=True)
    facebook_description = models.CharField(
        max_length=200, blank=True,
        help_text="Leave blank to use same text as summary.")
    facebook_message = models.TextField(
        blank=True, verbose_name="message",
        help_text="Longer status update that appears "
        "above the image in Facebook. ")
    facebook_send_status = models.CharField(max_length=20,
                                            choices=SCHEDULE_RESULTS,
                                            verbose_name="sent status",
                                            default="paused")
    last_tweeted = models.DateTimeField(
        default=timezone.make_aware(datetime.datetime(year=2000,
                                                      month=1, day=1)))
    # Logging
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(User, blank=True, null=True,
                             on_delete=models.CASCADE)
    version = models.PositiveIntegerField(default=0)

    # Author notifications and payments
    notified_authors = models.BooleanField(default=False)
    author_payment = models.DecimalField(default=0.00, max_digits=9,
                                         decimal_places=2)
    override_commissions_system = models.CharField(
        choices=OVERRIDE_COMMISSION_CHOICES, default="NO", max_length=20)
    commissions_processed = models.BooleanField(default=False)

    # Cached fields
    cached_byline = models.CharField(max_length=500, blank=True)
    cached_byline_no_links = models.CharField(max_length=400, blank=True,
                                              verbose_name="Byline")
    cached_primary_image = models.URLField(blank=True, max_length=500)
    cached_summary_image = models.URLField(blank=True, max_length=500)
    cached_summary_text = models.TextField(blank=True)
    cached_summary_text_no_html = models.TextField(blank=True)

    cached_small_image = models.URLField(blank=True, max_length=500)

    objects = ArticleQuerySet.as_manager()

    def is_published(self):
        return (self.published is not None) and \
            (self.published <= timezone.now())

    def publish_now(self):
        if self.is_published() is False:
            self.published = timezone.now()
            self.save()

    is_published.boolean = True
    is_published.short_description = 'published'

    def unsticky(self):
        self.stickiness = 0
        self.save()

    def make_top_story(self):
        articles = Article.objects.filter(stickiness__gt=0)
        for article in articles:
            article.stickiness = 0
            article.save()
        self.stickiness = 1
        self.save()

    # Methods that calculate cache fields

    '''Used to generate the cached byline upon model save, so
    there's less processing for website user requests.
    '''

    def calc_byline(self, links=False):
        if self.byline:
            return self.byline
        else:
            names = [self.author_01, self.author_02,
                     self.author_03, self.author_04,
                     self.author_05
                     ]
            if links:
                names = ["<a rel=\"author\" href='" + name.get_absolute_url() +
                         "'>" + str(name) + "</a>"
                         for name in names if name is not None]
            else:
                names = [str(name) for name in names if name is not None]
        # byline_style is Standard
        if self.byline_style == "ST" or len(names) != 2:
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
        # byline_style is TextByPhotoBy
        else:
            return "Text by " + names[0] + ". Photos by " + names[1] + "."

    '''Gets only the necessary part of primary image by URL. i.e. it removes
    the domain if the domain is in ALLOWED_HOSTS.
    '''
    def get_necessary_url(self, url):
        parsed_url = urlparse(url)
        if parsed_url[1] in django_settings.ALLOWED_HOSTS:
            return parsed_url[2]
        else:
            return url

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
        url = self.get_necessary_url(self.external_primary_image)
        return url

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

        if self.summary_image_alt == "":
            self.summary_image_alt = self.primary_image_alt

        if self.primary_image:
            if self.summary_image_size == 'LEAVE':
                return self.primary_image.url
            else:
                return self.primary_image.version_generate(image_size).url

        return self.cached_primary_image

    '''Used to generate the cached small image upon model save, so
    there's less processing for website user requests.
    '''

    def calc_small_image(self):
        if self.summary_image:
            return self.summary_image.version_generate("small").url

        if self.primary_image:
            return self.primary_image.version_generate("small").url

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

        if start_para[2] is None:
            return ""
        start_para = start_para[2].partition(">")

        if start_para[2] is None:
            return ""
        end_para = start_para[2].partition("</p>")

        if end_para[1] is None or end_para[0] is None:
            return ""
        return strip_tags(end_para[0])

    '''Legacy code from when more complex processing was done. But too
    time-consuming and server times out.
    '''

    def calc_summary_text_no_html(self):
        return strip_tags(self.cached_summary_text)

    def clean_typography(self, text):
        return smartypants.smartypants(text).\
            replace("&nbsp;", " ").\
            replace("  ", " ").\
            replace(u'&#8217;', u'’').\
            replace(u'&#8220;', u'“').\
            replace(u'&#8221;', u'”').\
            replace(u'\xa0 ', u' ').replace(u' \xa0', u' ')

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
        try:
            self.cached_small_image = self.calc_small_image()
        except:
            self.cached_small_image = ""
        self.title = self.clean_typography(self.title)
        self.subtitle = self.clean_typography(self.subtitle)
        self.primary_image_caption = \
            self.clean_typography(self.primary_image_caption)
        self.body = self.clean_typography(self.body)
        self.version = self.version + 1
        super(Article, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('newsroom:article.detail', args=[self.slug, ])

    def __str__(self):
        return str(self.pk) + " " + self.title

    def get_related(self, num_to_choose=3):
        return Article.objects.published().                         \
            exclude(pk=self.pk). \
            filter(topics__in=[self.main_topic]). \
            exclude(recommended=False)[:num_to_choose]

    def get_recommended(self, num_to_choose=3, days_back=10):
        publication_date = timezone.make_aware(
            datetime.datetime.now() - datetime.timedelta(days=days_back))
        return Article.objects.published().                         \
            filter(published__gt=publication_date).exclude(pk=self.pk). \
            exclude(recommended=False).order_by("?")[:num_to_choose]

    class Meta:
        ordering = ["-stickiness", "-published", ]



class UserEdit(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    changed = models.BooleanField(default=False)
    edit_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('article', 'user',)
        ordering = ['article__published', 'edit_time', ]

    def editStatusPlusName(self):
        if self.changed is True:
            suffix = " (changed)"
        else:
            suffix = ""
        s = str(self.user) + suffix
        return s

    def __str__(self):
        return ", ".join([str(self.article), str(self.user),
                          str(self.edit_time)])


class MostPopular(models.Model):
    '''This table's records each contain a list of the
    most popular articles as returned by the management command
    mostpopular.
    The latest (or only) record in this table can be obtained
    by views that display the most popular articles.
    The most popular articles are stored as a comma-delimited list
    in the article_list field.
    '''
    article_list = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.article_list[0:100]

    @staticmethod
    def get_most_popular_list():
        try:
            mostpopular = MostPopular.objects.latest("modified")
            article_list = mostpopular.article_list.split("\n")
            article_list = [item.split("|") for item in article_list]
        except MostPopular.DoesNotExist:
            article_list = None
        return article_list

    @staticmethod
    def get_most_popular_html():
        article_list = MostPopular.get_most_popular_list()
        if article_list is not None and len(article_list) > 1:
            try:
                html = "<ol class='most-popular'>"
                for article in article_list:
                    entry = "<li><a href='" + \
                            reverse('newsroom:article.detail', args=[article[0]]) + \
                            "'>" + article[1] + "</a></li>"
                    html = html + entry
                html = html + "</ol>"
            except:
                html = ""
        else:
            html = ""
        return html

    class Meta:
        verbose_name_plural = "most popular"

# Signals


@receiver(password_changed)
def set_password_reset(sender, **kwargs):
    author = kwargs["user"].author
    if author.password_changed is False:
        author.password_changed = True
        author.save()
