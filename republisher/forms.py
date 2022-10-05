from django import forms
from . import models

class RepublisherArticleForm(forms.ModelForm):

    class Meta:
        model = models.RepublisherArticle
        fields = ['republisher', 'status', ]

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.fields['republisher'].queryset = \
            models.Republisher.objects.filter(active=True)
