import re

from django import forms
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count, Sum
from django.db.models import F

from filebrowser.settings import ADMIN_VERSIONS, VERSIONS
from letters.admin import LetterInline
from payment.admin import CommissionInline, InvoiceInline
from republisher.admin import RepublisherInline
from socialmedia.admin import TweetInline
from socialmedia.common import SCHEDULE_RESULTS

from . import models, utils

# Used to select sizes of images
IMAGE_SIZE_CHOICES = [(item, VERSIONS[item]['verbose_name'],)
                      for item in ADMIN_VERSIONS]
IMAGE_SIZE_CHOICES.append(('LEAVE', 'LEAVE',))


# Regular expression to replace TinyMCE's pesky insertion of width
# and height attributes into images.

blankpara_regex = re.compile(r'<p[^>]*?>\s*?</p>|<p[^>]*?>\s*?&nbsp;\s*?</p>')

img_regex = re.compile(r'(<img(.*?))(height="(.*?)")(.*?)(width="(.*?)")(.*?)(>)')

figure_regex = re.compile(r'(<p>)(.*?)(<img)(.*?)(/>)(.*?)(</p>)(.*?)\r\n(<p) (class="caption")(.*?)>(.*?)(</p>)')


class CorrectionInline(admin.StackedInline):
    model = models.Correction
    extra = 0


class ArticleForm(forms.ModelForm):
    summary_image_size = forms.ChoiceField(choices=IMAGE_SIZE_CHOICES,
                                           initial="medium")
    # primary_image_size = forms.ChoiceField(choices=IMAGE_SIZE_CHOICES,
    #                                       initial="extra_large")

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
                       ('byline', 'byline_style', ),
                       'editor_feedback')
        }),
        ('Content', {
            'classes': ('wide',),
            'fields': ('body', )
        }),
        ('Publish', {
            'fields': ('category', 'topics', 'main_topic',
                       'region', ('recommended',  'undistracted_layout', ),
                       'slug', 'published', ),
        }),
        ('Summary Image and text', {
            'classes': ('grp-collapse grp-closed',),
            'fields': (
                'summary_image', 'summary_image_size',
                'summary_image_alt', 'cached_summary_text',
                'summary_text', 'summary_template',),
        }),
        ('Advanced', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('copyright', 'include_in_rss',
                       ('letters_on', 'comments_on', 'collapse_comments', ),
                       'stickiness', 'exclude_from_list_views',
                       'use_editor',
                       ('template', 'template_process', ),
                       'additional_head_scripts', 'additional_body_scripts',
                       'activate_slideshow',
                       ('last_tweeted', 'notified_authors',),
                       ('author_payment', 'override_commissions_system',
                        'commissions_processed',),
                       ('suppress_ads', 'promote_article',
                        'encourage_republish',),
                       ('user', 'modified', 'version'),
                       ('secret_link', 'secret_link_view',))
        })
    )

    inlines = [
        TweetInline, RepublisherInline, CorrectionInline,
        LetterInline, # CommissionInline,
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
            '//cdn.ckeditor.com/4.14.0/standard-all/ckeditor.js',
            '/static/newsroom/js/ck_styles.js?v=20220203',
            '/static/newsroom/js/ck_init_admin.js?v=20220203',
            '/static/newsroom/js/statistics.js?v=20220203',
            '/static/newsroom/js/admin_enhance.js?v=20220203',
            '/static/socialmedia/js/tweets.js?v=20220203',
        ]


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


class RegionAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


class TopicAdmin(admin.ModelAdmin):
    search_fields = ['name', 'slug', ]
    list_display = ('name', 'num_articles', 'num_qanda' )
    prepopulated_fields = {"slug": ("name", )}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            num_articles=Count('article', distinct=True),
            num_qanda=Count('qanda', distinct=True)
        )
        return queryset

    def num_articles(self, obj):
        return obj.num_articles

    num_articles.admin_order_field = 'num_articles'

    def num_qanda(self, obj):
        return obj.num_qanda

    num_qanda.admin_order_field = 'num_qanda'

    def total(self, obj):
        return obj.total

    total.admin_order_field = 'total'



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
    list_display = ('last_name', 'first_names', 'created',
                    'email', 'freelancer', 'level', )
    list_editable = ('email', 'freelancer','level', )
    search_fields = ['last_name', 'first_names', ]
    # inlines = [
    #    InvoiceInline,
    # ]
    raw_id_fields = ('user', )
    autocomplete_lookup_fields = {
        'fk': ['user',],
    }

class CorrectionAdmin(admin.ModelAdmin):
    list_display = ('article', 'update_type', 'created', 'modified',)
    list_editable = ('update_type', )
    list_filter = ['update_type', ]
    ordering = ['-modified', ]
    search_fields = ['text', 'article__title', ]
    raw_id_fields = ('article',)
    autocomplete_lookup_fields = {
        'fk': ['article',],
    }

admin.site.register(models.Author, AuthorAdmin)
admin.site.register(models.MostPopular)
admin.site.register(models.Correction, CorrectionAdmin)

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
            '//cdn.ckeditor.com/4.14.0/standard-all/ckeditor.js',
            '/static/newsroom/js/ck_styles.js',
            '/static/newsroom/js/ck_init_admin.js',
        ]


# Re-register FlatPageAdmin
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
