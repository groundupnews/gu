from django import forms
from django.forms import widgets

class ArticleListForm(forms.Form):
    date_from = forms.DateTimeField()
    date_to = forms.DateTimeField(required=False)


class ArticleForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea)
