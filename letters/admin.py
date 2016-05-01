from django.contrib import admin

from . import models


class LetterAdmin(admin.ModelAdmin):
    list_display = ['article', 'byline', 'email', 'title',
                    'rejected', 'published', 'is_published', ]
    list_filter = ['rejected', ]
    search_fields = ['article__title', 'title', 'byline', 'email', ]
    ordering = ['article__modified', '-position', ]


admin.site.register(models.Letter, LetterAdmin)


class LetterInline(admin.StackedInline):
    model = models.Letter
    classes = ('grp-closed',)
    extra = 0
