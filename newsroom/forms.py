from django import forms

from . import models, utils


SEARCH_TYPES=[('article', 'Articles'),
             ('image', 'Images'),
             ('both', 'Both')]

class ArticleListForm(forms.Form):
    date_from = forms.DateTimeField()
    date_to = forms.DateTimeField(required=False)


class ArticleForm(forms.ModelForm):

    def clean(self, *args, **kwargs):
        if self.cleaned_data["use_editor"]:
            body = self.cleaned_data["body"]
            self.cleaned_data["body"] = utils.replaceBadHtmlWithGood(body)

        super(ArticleForm, self).clean(*args, **kwargs)

    class Meta:
        model = models.Article
        fields = ['title', 'subtitle', 'use_editor',
                  'primary_image_caption', 'body', 'user', 'version', ]


class AdvancedSearchForm(forms.Form):
    RESULTS_PER_PAGE = [(10, '10 Results Per Page'),
                        (20, '20 Results Per Page'),
                        (50, '50 Results Per Page'),
                        (100, '100 Results Per Page')]
    
    adv_search = forms.CharField(label="Search Term...",
                                 widget=forms.TextInput(attrs={'placeholder': 'Search...'}),
                                 required=False)
    search_type = forms.ChoiceField(choices=SEARCH_TYPES,
                                    widget=forms.RadioSelect(),
                                    required=False,
                                    initial='both')
    author = forms.ModelChoiceField(queryset=models.Author.objects.all().order_by('first_names'),
                                    required=False)
    first_author = forms.BooleanField(label="First Author Only", required=False)
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), required=False)
    topics = forms.ModelChoiceField(queryset=models.Topic.objects.all(), required=False)
    date_from = forms.DateTimeField(widget=forms.DateInput(attrs={'data-toggle': 'datepicker'}),
                                    required=False,
                                    input_formats=['%d/%m/%Y'])
    date_to = forms.DateTimeField(widget=forms.DateInput(attrs={'data-toggle': 'datepicker'}),
                                  required=False,
                                  input_formats=['%d/%m/%Y'])
    results_per_page = forms.ChoiceField(choices=RESULTS_PER_PAGE, required=False)
