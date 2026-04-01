from django.contrib import admin
from . import models


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


class RepublisherInline(admin.TabularInline):
    model = models.RepublisherArticle
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
