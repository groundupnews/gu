from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from . import models


def check_date(cleaned_data):
    if cleaned_data['accept_event_date'] is True and \
        not cleaned_data['event_date']:
        raise ValidationError("Event date cannot be blank if accepted.");


class EventAdminForm(forms.ModelForm):

    def clean(self):
        self.cleaned_data = super().clean()
        check_date(self.cleaned_data)
        return self.cleaned_data

class EventAdminFormSet(forms.BaseModelFormSet):

    def clean(self):
        form_set = self.cleaned_data
        for form_data in form_set:
            check_date(form_data)
        return form_set

class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ('case_id', 'process_status',
                    'event_type', 'accept_event_type', 'email_address',
                    'event_date', 'accept_event_date', 'created', 'modified',)
    list_editable = ('process_status', 'event_type', 'accept_event_type',
                     'event_date', 'accept_event_date' )
    search_fields = ('case_id', 'judges', 'email_address',)
    list_filter = ('process_status',)
    ordering = ('-modified', )

    def get_changelist_formset(self, request, **kwargs):
        kwargs['formset'] = EventAdminFormSet
        return super().get_changelist_formset(request, **kwargs)

admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Court)
