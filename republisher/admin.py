from django.contrib import admin
from . import models

admin.site.register(models.Republisher)
admin.site.register(models.RepublisherArticle)

class RepublisherInline(admin.TabularInline):
    model = models.RepublisherArticle
    classes = ('grp-collapse grp-closed',)
    extra = 1
