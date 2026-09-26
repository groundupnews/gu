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
             ('video', 'Videos'),
             ('image', 'Images'),
             ('both', 'Everything')]

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


class VideoForm(forms.ModelForm):
    youtube_id = forms.CharField(
        label='YouTube URL',
        help_text='Paste the watch URL. A Short URL works too.',
        widget=forms.TextInput(
            attrs={'placeholder': 'https://www.youtube.com/watch?v=...'}))
    authors = AutoCompleteSelectMultipleField(
        "authors", required=False, help_text=None, label="Authors")
    topics = AutoCompleteSelectMultipleField("topics", required=False,
                                             help_text=None, label="Topics")
    related_articles = AutoCompleteSelectMultipleField(
        "articles", required=False, help_text=None, label="Related articles")
    published = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'},
                                   format='%Y-%m-%dT%H:%M'),
        help_text='Leave blank to keep the video off the site.')
    # Plain text rather than the filebrowser widget
    thumbnail = forms.CharField(
        required=False,
        help_text='Path under the media directory. Leave blank to use the '
                  'thumbnail YouTube generates.')

    class Meta:
        model = models.Video
        fields = [
            'title', 'slug', 'youtube_id', 'category',
            'summary', 'body', 'duration', 'authors', 'byline', 'credits',
            'thumbnail', 'thumbnail_alt', 'topics', 'related_articles',
            'published', 'promote', 'include_on_home', 'pin_to_home',
            'copyright',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'body': forms.Textarea(attrs={'rows': 10,
                                          'class': 'gu-ckeditor'}),
            'credits': forms.Textarea(attrs={'rows': 2}),
            'copyright': forms.Textarea(attrs={'rows': 3}),
        }


# The timecode format is validated by the model field's validator
VideoChapterFormSet = forms.inlineformset_factory(
    models.Video, models.VideoChapter, fields=['timecode', 'description'],
    help_texts={'timecode': '', 'description': ''},
    extra=4, can_delete=True)


class VideoRolesField(forms.MultipleChoiceField):
    """Role checkboxes, stored as comma-separated keys."""

    def __init__(self, **kwargs):
        kwargs.setdefault('choices', models.VIDEO_ROLE_CHOICES)
        kwargs.setdefault('widget', forms.CheckboxSelectMultiple)
        super().__init__(**kwargs)

    def prepare_value(self, value):
        if isinstance(value, str):
            return models.split_roles(value)
        return value

    def clean(self, value):
        return models.join_roles(super().clean(value))

    def has_changed(self, initial, data):
        # Initial is a string, data a list. Without this a blank extra row
        # looks edited.
        if isinstance(initial, str):
            initial = models.split_roles(initial)
        return super().has_changed(initial, data)


class VideoContributorForm(forms.ModelForm):
    """One row of the credits. The author has to be on system!"""

    author = AutoCompleteSelectField("authors", help_text=None, label="Person")
    # Optional so blank rows validate; clean() needs it once a person is set.
    roles = VideoRolesField(required=False, label="What they did")

    class Meta:
        model = models.VideoContributor
        fields = ['author', 'roles', 'note', 'position', 'no_payment', ]
        help_texts = {'roles': '', 'note': '', 'position': '',
                      'no_payment': ''}

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('author') and not cleaned_data.get('roles'):
            self.add_error('roles', 'Tick at least one job.')
        return cleaned_data


VideoContributorFormSet = forms.inlineformset_factory(
    models.Video, models.VideoContributor, form=VideoContributorForm,
    extra=3, can_delete=True)
