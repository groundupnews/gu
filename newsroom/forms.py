from django import forms
from . import models

class ArticleListForm(forms.Form):
    date_from = forms.DateTimeField()
    date_to = forms.DateTimeField(required=False)


class ArticleForm(forms.ModelForm):

    class Meta:
        model = models.Article
        fields = ['title', 'subtitle', 'primary_image_caption', 'body',]
