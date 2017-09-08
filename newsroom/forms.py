from django import forms
from . import models
from . import utils


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
