from django import forms
from django.forms import ModelForm
from . import models


class EventAddForm(ModelForm):

    class Meta:
        model = models.Event
        fields = ('case_id', 'email_address', 'event_type',
                  'event_date', 'court', 'case_name', 'judges',
                  'document_url', 'document', 'notes')
        widgets = {
          'case_id': forms.TextInput(attrs={'autofocus': True}),
          'judges': forms.Textarea(attrs={'rows':3, 'cols':40}),
          'notes': forms.Textarea(attrs={'rows':3, 'cols':40}),
          'event_date': forms.DateInput(attrs={'type': 'date'})
        }
