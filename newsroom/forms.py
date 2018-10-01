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
    adv_search = forms.CharField(label="Search",
                                widget=forms.TextInput(attrs={'placeholder': 'Search...'}))
    search_type = forms.ChoiceField(choices=SEARCH_TYPES, widget=forms.RadioSelect())
    category = forms.ModelChoiceField(queryset=models.Category.objects.all())
    topics = forms.ModelChoiceField(queryset=models.Topic.objects.all())
    date_from = forms.DateTimeField()
    date_to = forms.DateTimeField()
