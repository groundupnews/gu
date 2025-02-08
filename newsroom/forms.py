from ajax_select.fields import AutoCompleteSelectField
from ajax_select.fields import AutoCompleteSelectMultipleField
from ajax_select import make_ajax_field
from django import forms
from django.utils.html import strip_tags
from filebrowser.settings import ADMIN_VERSIONS, VERSIONS
from . import models, utils
from newsroom.settings import SEARCH_MAXLEN

IMAGE_SIZE_CHOICES = [(item, VERSIONS[item]['verbose_name'],)
                      for item in ADMIN_VERSIONS]
IMAGE_SIZE_CHOICES.append(('LEAVE', 'LEAVE',))

SEARCH_TYPES=[('article', 'Articles'),
             ('image', 'Images'),
             ('both', 'Both')]

class AuthorForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = models.Author
        fields = [
            'first_names', 'last_name', 'freelancer', 'level', 'email',
            'allowance',
        ]


class ArticleListForm(forms.Form):
    date_from = forms.DateField()
    date_to = forms.DateField(required=False)


article_ajaxes = ['author_01',  'author_02', 'author_03',
                  'author_04', 'author_05', 'topics', 'main_topic', ]

article_inputs = article_ajaxes + \
    ['published', 'category', 'region',
     'byline', 'byline_style', 'editor_feedback',
     'slug', 'recommended', 'include_in_rss', 'use_editor', 'stickiness',
     'summary_image', 'summary_image_size', 'summary_image_alt','audio_summary','audio_publish', 'summary_text',
     'exclude_from_list_views', 'promote_article', 'letters_on',
     'stickiness', 'secret_link', 'secret_link_view',
     'encourage_republish', 'additional_head_scripts', 'additional_body_scripts', ]

article_specials = ['version', ]

article_contenteditables = ['title', 'subtitle',
                            'primary_image_caption',
                            'body', 'copyright', ]

article_form_fields =  article_inputs + article_contenteditables + \
    article_specials

class ArticleForm(forms.ModelForm):
    author_01 = AutoCompleteSelectField("authors", required=False,
                                        help_text=None, label="First author")
    author_02 = AutoCompleteSelectField("authors", required=False,
                                        help_text=None, label="Second author")
    author_03 = AutoCompleteSelectField("authors", required=False,
                                        help_text=None, label="Third author")
    author_04 = AutoCompleteSelectField("authors", required=False,
                                        help_text=None, label="Fourth author")
    author_05 = AutoCompleteSelectField("authors", required=False,
                                        help_text=None, label="Fifth author")
    main_topic = AutoCompleteSelectField("topics", required=False,
                                        help_text=None, label="Main topic")
    topics = AutoCompleteSelectMultipleField("topics", required=False,
                                             help_text=None, label="Topics")
    summary_image = forms.CharField(required=False)
    summary_image_size = forms.ChoiceField(choices=IMAGE_SIZE_CHOICES)

    audio_summary=forms.CharField(required=False)
    audio_publish=forms.BooleanField(required=False)
    btn_unsticky = forms.CharField(required=False, label='Unsticky',
                                widget=forms.TextInput(
                                attrs={'class': 'button-action',
                                       'data-visible': 'stickiness'}))
    btn_top_story = forms.CharField(required=False, label='Top story',
                                    widget=forms.TextInput(
                                    attrs={'class': 'button-action',
                                           'data-not': '1',
                                           'data-visible': 'stickiness'}))

    btn_full_width = forms.CharField(required=False, label='Full width',
                                    widget=forms.TextInput(
                                    attrs={'class': 'button-action',
                                        'data-not': '1',
                                        'data-visible': 'undistracted_layout'}))
    btn_half_width = forms.CharField(required=False, label='Half width',
                                    widget=forms.TextInput(
                                    attrs={'class': 'button-action',
                                           'data-visible': 'undistracted_layout'}))

    btn_secret_link = forms.CharField(required=False, label='Make private URL',
                                    widget=forms.TextInput(
                                    attrs={'class': 'button-action',
                                        'data-visible': 'secret_linkable'}))

    btn_publish_now = forms.CharField(required=False, label='Publish',
                                    widget=forms.TextInput(
                                    attrs={'class': 'button-action',
                                        'data-visible': 'is_published',
                                        'data-not': '1'}))

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        fields = [f for f in self.visible_fields()
                  if f.name in article_form_fields]
        for field in fields:
            field.field.widget.attrs['placeholder'] = field.label;
            field.field.widget.attrs['data-article-form'] = "y";
            if field.name in article_contenteditables:
                field.field.widget.attrs['data-type'] = 'contenteditable'
                if field.name in ['title',]:
                    pass
                elif field.name in ['subtitle']:
                    field.field.widget.attrs['data-editor'] = \
                        'ck_inline_basic_config.js?v=20220204g'
                else:
                    field.field.widget.attrs['data-editor'] = \
                        'ck_inline_config.js?v=20220204g'
            elif field.name in article_inputs:
                field.field.widget.attrs['data-type'] = 'input'
                field.field.widget.attrs['data-display'] = 'inline';
                if field.name in article_ajaxes:
                    field.field.widget.attrs['data-ajax'] = 'y'

    class Meta:
        model = models.Article
        fields = article_form_fields

class ArticleNewForm(forms.ModelForm):

    class Meta:
        model = models.Article
        fields = ['title', 'slug',]

class AdvancedSearchForm(forms.Form):
    RESULTS_PER_PAGE = [(10, '10 Results Per Page'),
                        (20, '20 Results Per Page'),
                        (50, '50 Results Per Page'),
                        (100, '100 Results Per Page')]

    adv_search = forms.CharField(label="Search Term...",
                                 widget=forms.TextInput(
                                     attrs={
                                         'placeholder': 'Search...',
                                         'maxlength': SEARCH_MAXLEN,
                                     }),
                                 required=False)
    search_type = forms.ChoiceField(choices=SEARCH_TYPES,
                                    widget=forms.RadioSelect(),
                                    required=False,
                                    initial='both')
    author = AutoCompleteSelectField("authors_only", required=False,
                                     help_text=None, label="Author")

    def clean_author(self):
        try:
            author = self.cleaned_data.get('author')
            if author and isinstance(author, models.Author):
                return author
        except (ValueError, TypeError, AttributeError):
            pass
        return None

    first_author = forms.BooleanField(label="First author only", required=False)
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), required=False)
    topics = forms.ModelChoiceField(queryset=models.Topic.objects.all(), required=False)
    date_from = forms.DateTimeField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateTimeField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    results_per_page = forms.ChoiceField(choices=RESULTS_PER_PAGE, required=False)
