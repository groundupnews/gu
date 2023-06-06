from django import forms
from django.forms import ModelForm
from . import models


class EventAddForm(ModelForm):

    class Meta:
        model = models.Event
        fields = ('case_number', 'email_address', 'event_type', 'court',
                  'event_date', 'case_name', 'judges',
                  'document_url', 'document', 'notes')
        widgets = {
          'case_number': forms.TextInput(attrs={'autofocus': True}),
          'judges': forms.Textarea(attrs={'rows':3, 'cols':40}),
          'notes': forms.Textarea(attrs={'rows':3, 'cols':40}),
          'event_date': forms.DateInput(attrs={'data-toggle': 'datepicker'})
        }
