from django.contrib import admin
from django import forms
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from payment.admin import InvoiceInline, CommissionInline
import re

from . import models
from . import utils

from socialmedia.admin import TweetInline
from socialmedia.common import SCHEDULE_RESULTS
from republisher.admin import RepublisherInline
from letters.admin import LetterInline

from filebrowser.settings import ADMIN_VERSIONS, VERSIONS

# Used to select sizes of images
IMAGE_SIZE_CHOICES = [(item, VERSIONS[item]['verbose_name'],)
                      for item in ADMIN_VERSIONS]
IMAGE_SIZE_CHOICES.append(('LEAVE', 'LEAVE',))


# Regular expression to replace TinyMCE's pesky insertion of width
# and height attributes into images.

blankpara_regex = re.compile(r'<p[^>]*?>\s*?</p>|<p[^>]*?>\s*?&nbsp;\s*?</p>')

img_regex = re.compile(r'(<img(.*?))(height="(.*?)")(.*?)(width="(.*?)")(.*?)(>)')

figure_regex = re.compile(r'(<p>)(.*?)(<img)(.*?)(/>)(.*?)(</p>)(.*?)\r\n(<p) (class="caption")(.*?)>(.*?)(</p>)')


class ArticleForm(forms.ModelForm):
    summary_image_size = forms.ChoiceField(choices=IMAGE_SIZE_CHOICES,
                                           initial="medium")
    primary_image_size = forms.ChoiceField(choices=IMAGE_SIZE_CHOICES,
                                           initial="extra_large")
    facebook_send_status = forms.ChoiceField(choices=SCHEDULE_RESULTS,
                                             initial="scheduled")
    '''Remove height and width from TinyMCE image insertions.
    '''

    def clean_main_topic(self):
        if self.cleaned_data["main_topic"] == "(None)":
            self.cleaned_data["main_topic"] = None
        return self.cleaned_data["main_topic"]

    def clean(self, *args, **kwargs):

        if self.instance.pk:
            if self.instance.version > self.cleaned_data["version"]:
                raise ValidationError(utils.get_edit_lock_msg(
                    self.instance.user))

        if self.cleaned_data["main_topic"]:
            self.cleaned_data["topics"] = self.cleaned_data["topics"] | \
                    models.Topic.objects.filter(
                        name=self.cleaned_data["main_topic"])

        # Transform the body to fix Wysiwyg editor limitations

        if self.cleaned_data["use_editor"]:
            body = self.cleaned_data["body"]
            self.cleaned_data["body"] = utils.replaceBadHtmlWithGood(body)

        super(ArticleForm, self).clean(*args, **kwargs)


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
    list_display = ('title', 'created', 'modified', 'published',
                    'is_published', 'cached_byline_no_links', 'category',)
    prepopulated_fields = {"slug": ("title", )}
    search_fields = ['title', 'cached_byline_no_links', ]
    date_hierarchy = 'modified'
    ordering = ['-modified', ]
    list_filter = ['published', 'category', 'region', 'topics']
    raw_id_fields = ('author_01', 'author_02', 'author_03', 'author_04',
                     'author_05', 'topics', 'main_topic', )
    autocomplete_lookup_fields = {
        'fk': ['author_01', 'author_02', 'author_03',
               'author_04', 'author_05', 'main_topic', ],
        'm2m': ['topics', ]
    }

    readonly_fields = ('cached_byline_no_links', 'cached_summary_text',
                       'user', 'modified', )

    fieldsets = (
        ('Identifying Information', {
            'classes': ('wide',),
            'fields': ('title', 'subtitle', 'cached_byline_no_links',
                       'author_01',)
        }),
        ('Additional authors', {
            'classes': ('wide grp-collapse grp-closed',),
            'fields': ('author_02', 'author_03', 'author_04', 'author_05',
                       ('byline', 'byline_style', ))
        }),
        ('Primary Image', {
            'classes': ('wide',),
            'fields': (('primary_image', 'primary_image_size', ),
                       ('external_primary_image'),
                       'primary_image_caption', 'primary_image_alt', )
        }),
        ('Content', {
            'classes': ('wide',),
            'fields': ('body', )
        }),
        ('Publish', {
            'fields': ('category', 'topics', 'main_topic',
                       'region', 'recommended', 'slug', 'published', ),
        }),
        ('Summary', {
            'classes': ('grp-collapse grp-closed',),
            'fields': (('summary_image', 'summary_image_size', ),
                       'summary_image_alt', 'cached_summary_text',
                       'summary_text', 'summary_template',),
        }),
        ('Advanced', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('copyright', 'include_in_rss',
                       ('letters_on', 'comments_on', 'collapse_comments', ),
                       'stickiness', 'exclude_from_list_views',
                       'use_editor',
                       ('template', 'undistracted_layout', ),
                       'additional_head_scripts', 'additional_body_scripts',
                       'activate_slideshow',
                       ('last_tweeted', 'notified_authors',),
                       ('author_payment', 'override_commissions_system',
                        'commissions_processed',),
                       ('suppress_ads', 'promote_article',
                        'encourage_republish',),
                       ('user', 'modified', 'version'),)
        }),
        ('Facebook', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('facebook_wait_time', 'facebook_image',
                       'facebook_image_caption',
                       'facebook_description', 'facebook_message',
                       'facebook_send_status', ), })
    )

    inlines = [
        TweetInline, RepublisherInline, LetterInline, CommissionInline,
    ]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        return super(ArticleAdmin, self).\
            changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    class Media:
        css = {'all': ('/static/newsroom/css/admin_enhance.css', )}
        js = [
            '//cdn.ckeditor.com/4.7.3/standard-all/ckeditor.js',
            '/static/newsroom/js/ck_styles.js',
            '/static/newsroom/js/ck_init_admin.js',
            '/static/newsroom/js/admin_enhance.js',
            '/static/socialmedia/js/tweets.js',
        ]


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


class RegionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'count_articles', )
    prepopulated_fields = {"slug": ("name", )}


admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.UserEdit)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Region, RegionAdmin)
admin.site.register(models.Topic, TopicAdmin)


class AuthorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True


class AuthorAdmin(admin.ModelAdmin):
    form = AuthorForm
    list_display = ('last_name', 'first_names', 'created', 'modified',
                    'email', 'cell', 'freelancer', )
    list_editable = ('email', 'cell', 'freelancer',)
    search_fields = ['last_name', 'first_names', ]
    inlines = [
        InvoiceInline,
    ]
    raw_id_fields = ('user', )
    autocomplete_lookup_fields = {
        'fk': ['user',],
    }

admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.MostPopular)

# Define a new FlatPageAdmin
class FlatPageAdmin(FlatPageAdmin):
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'sites')}),
        (_('Advanced options'), {
            'classes': ('collapse', ),
            'fields': (
                'registration_required',
                'template_name',
            ),
        }),
    )

    class Media:
        css = {'all': ('/static/newsroom/css/admin_enhance.css', )}
        js = [
            '//cdn.ckeditor.com/4.7.3/standard-all/ckeditor.js',
            '/static/newsroom/js/ck_styles.js',
            '/static/newsroom/js/ck_init_admin.js',
        ]


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
