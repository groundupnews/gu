from django import forms
from django.db.models import Q
from . import models


def selectable_republishers(instance):
    """Active republishers, plus the instance's current republisher (even if
    it has since been deactivated) so that existing rows remain valid."""
    if instance.pk and instance.republisher_id:
        return models.Republisher.objects.filter(
            Q(active=True) | Q(pk=instance.republisher_id)
        )
    return models.Republisher.objects.filter(active=True)


class RepublisherArticleForm(forms.ModelForm):

    class Meta:
        model = models.RepublisherArticle
        fields = ['republisher', 'status', ]

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self.fields['republisher'].queryset = \
            selectable_republishers(self.instance)
