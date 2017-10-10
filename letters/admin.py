from django.contrib import admin
from django import forms

from . import models


class ProcessedListFilter(admin.SimpleListFilter):
    title = 'processed'
    parameter_name = 'processed'

    def lookups(self, request, model_admin):
        return (
            ('published', 'published'),
            ('rejected', 'rejected'),
            ('processed', 'processed'),
            ('unprocessed', 'unprocessed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'published':
            return queryset.published()
        if self.value() == 'rejected':
            return queryset.filter(rejected=True)
        if self.value() == 'processed':
            return queryset.published() | queryset.filter(rejected=True)
        if self.value() == 'unprocessed':
            return queryset.filter(published__isnull=True).\
                filter(rejected=False)


class LetterForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(LetterForm, self).clean()
        rejected = cleaned_data.get("rejected")
        published = cleaned_data.get("published")

        if rejected is True and published is not None:
            raise forms.ValidationError(
                "Please either check rejected or set a "
                "publication date, but not both."
            )


class LetterAdmin(admin.ModelAdmin):
    form = LetterForm
    list_display = ['article', 'byline', 'email', 'title',
                    'rejected', 'published', 'modified', ]
    date_hierarchy = 'modified'
    list_filter = [ProcessedListFilter, ]
    search_fields = ['article__title', 'title', 'byline', 'email', ]
    ordering = ['-modified', '-position', ]
    raw_id_fields = ('article', )


admin.site.register(models.Letter, LetterAdmin)


class LetterInline(admin.StackedInline):
    model = models.Letter
    classes = ('grp-closed',)
    extra = 0
