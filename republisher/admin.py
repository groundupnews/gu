from django import forms
from django.contrib import admin
from . import models
from .forms import selectable_republishers


class RepublisherAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "name",
        "active",
        "ask_for_analytics",
        "email_addresses",
    ]
    list_editable = [
        "name",
        "active",
        "ask_for_analytics",
        "email_addresses",
    ]


admin.site.register(models.Republisher, RepublisherAdmin)


class RepublisherInlineForm(forms.ModelForm):
    class Meta:
        model = models.RepublisherArticle
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["republisher"].queryset = selectable_republishers(self.instance)


class RepublisherInline(admin.TabularInline):
    model = models.RepublisherArticle
    form = RepublisherInlineForm
    verbose_name = "republisher"
    verbose_name_plural = "republishers"
    classes = ("grp-collapse grp-closed",)
    extra = 1


class RepublisherArticleAdmin(admin.ModelAdmin):
    list_display = [
        "article",
        "published",
        "republisher",
        "status",
    ]
    ordering = [
        "article__published",
    ]


admin.site.register(models.RepublisherArticle, RepublisherArticleAdmin)
