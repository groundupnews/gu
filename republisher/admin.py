from django.contrib import admin
from . import models

admin.site.register(models.Republisher)
admin.site.register(models.RepublisherArticle)

class RepublisherInline(admin.TabularInline):
    model = models.RepublisherArticle
    verbose_name = "republisher"
    verbose_name_plural = "republishers"
    classes = ('grp-collapse grp-closed',)
    extra = 1
