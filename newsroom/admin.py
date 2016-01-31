from django.contrib import admin
from django import forms
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, Textarea

import re

from . import models
from . import utils
from socialmedia.models import Tweet
from socialmedia.admin import TweetInline
from republisher.admin import RepublisherInline

import tagulous
from filebrowser.settings import ADMIN_VERSIONS, VERSIONS


# Used to select sizes of images
IMAGE_SIZE_CHOICES = [(item, VERSIONS[item]['verbose_name'],)  \
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
                                           initial="large")

    '''Remove height and width from TinyMCE image insertions.
    '''

    def clean_main_topic(self):
        if self.cleaned_data["main_topic"] == "(None)":
            self.cleaned_data["main_topic"] = None
        return self.cleaned_data["main_topic"]

    def clean(self, *args, **kwargs):

        if self.cleaned_data["main_topic"]:
            topic = self.cleaned_data["main_topic"]
            if topic not in self.cleaned_data["topics"]:
                self.cleaned_data["topics"].append(topic)

        # Transform the body to fix Wysiwyg editor limitations

        if self.cleaned_data["use_editor"]:
            body = self.cleaned_data["body"]
            self.cleaned_data["body"] = utils.replaceBadHtmlWithGood(body)

        super(ArticleForm, self).clean(*args, **kwargs)


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
    list_display = ('title', 'created', 'modified', 'published',
                    'is_published', 'cached_byline_no_links', 'category',)
    prepopulated_fields = {"slug": ("title",) }
    search_fields = ['title', 'cached_byline_no_links',]
    date_hierarchy = 'modified'
    ordering = ['-modified',]
    list_filter = ['published', 'category', 'region', 'topics']
    raw_id_fields = ('author_01','author_02', 'author_03', \
                     'author_04', 'author_05',)
    autocomplete_lookup_fields = {
        'fk': ['author_01', 'author_02', 'author_03', \
                'author_04', 'author_05',],
    }

    readonly_fields=('cached_byline_no_links',
                     'cached_summary_text',)

    fieldsets = (
        ('Identifying Information', {
            'classes': ('wide',),
            'fields': ('title', 'subtitle', 'cached_byline_no_links',
                       'author_01',)
        }),
        ('Additional authors', {
            'classes': ('wide grp-collapse grp-closed',),
            'fields': ('author_02', 'author_03', 'author_04', 'author_05',)
        }),
        ('Primary Image', {
            'classes': ('wide',),
            'fields': ( ('primary_image', 'primary_image_size',),
                        'primary_image_caption', 'primary_image_alt',)
        }),
        ('External URL for primary image', {
            'classes': ('grp-collapse grp-closed',),
            'fields':('external_primary_image',)
        }),
        ('Content', {
            'classes': ('wide',),
            'fields': ( 'body', )
        }),
        ('Publish', {
            'fields': ('category', 'topics', 'main_topic',
                       'region', 'slug', 'published', ),
        }),
        ('Summary', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ( ('summary_image', 'summary_image_size',),
                        'summary_image_alt', 'cached_summary_text',
                        'summary_text', 'summary_template',),
        }),
        ('Advanced', {
            'classes': ('grp-collapse grp-closed',),
            'fields':('copyright', 'include_in_rss', 'comments_on',
                      'stickiness', 'exclude_from_list_views',
                      'recommended', 'byline', 'use_editor',
                      'template', 'disqus_id',)
        }),
        ('Facebook', {
            'classes': ('grp-collapse grp-closed',),
            'fields':(
                'facebook_wait_time', 'facebook_image', 'facebook_image_caption',
                'facebook_description', 'facebook_message',
                'facebook_send_status',
            ),
        })
    )

    inlines = [
        TweetInline, RepublisherInline
    ]
    def get_changeform_initial_data(self, request):
        return {'category': 'News'}

    class Media:
        css = { 'all' : ('/static/newsroom/css/admin_enhance.css',)}
        js = [
            '//cdn.ckeditor.com/4.5.6/standard-all/ckeditor.js',
            '/static/newsroom/js/ck_styles.js',
            '/static/newsroom/js/ck_init_admin.js',
            '/static/newsroom/js/admin_enhance.js',
            '/static/socialmedia/js/tweets.js',
        ]

admin.site.register(models.Article, ArticleAdmin)
tagulous.admin.register(models.Category)
tagulous.admin.register(models.Region)
tagulous.admin.register(models.Topic)

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_names', 'created', 'modified',
                    'email', 'telephone', 'cell', )
    search_fields = ['last_name', 'first_names',]

admin.site.register(models.Author, AuthorAdmin)

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
        css = { 'all' : ('/static/newsroom/css/admin_enhance.css',) }
        js = [
            '//cdn.ckeditor.com/4.5.6/standard-all/ckeditor.js',
            '/static/newsroom/js/ck_styles.js',
            '/static/newsroom/js/ck_init_admin.js',
        ]



# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
