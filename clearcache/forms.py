from django import forms

class ClearCacheForm(forms.Form):
    keys = forms.CharField(label='Cache keys if any', max_length=100,
                                required=False)
