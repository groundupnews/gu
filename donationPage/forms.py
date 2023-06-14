from ajax_select.fields import AutoCompleteSelectField
from ajax_select.fields import AutoCompleteSelectMultipleField
from ajax_select import make_ajax_field
from django import forms
from django.utils.html import strip_tags
from filebrowser.settings import ADMIN_VERSIONS, VERSIONS
from . import models, utils
from newsroom.settings import SEARCH_MAXLEN


class DonorForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=50)
    display_name = forms.CharField(max_length=50)
    #donor_url = forms.CharField(max_length=60)
    
    class Meta:
        model = models.Donor
        fields = ['name', 'display_name', 'email',]

class CurrencyForm(forms.ModelForm):
    currency_abr=forms.CharField(max_length=100)
    
    class Meta:
        model = models.Currency
        fields = ['currency_abr']

class DonationForm(forms.ModelForm):
    donation_date = forms.DateTimeField()
    #donor = forms.ForeignKey(Donor, on_delete=models.CASCADE)
    #donor = AutoCompleteSelectField("donors", required=True, help_text=None, label="donor")
    #platform = forms.ForeignKey(Platform,  on_delete=models.CASCADE)
    recurring = forms.BooleanField()
    donation_amount = forms.IntegerField()
    currency_type = forms.CharField(max_length=4)
    #certificate_issued = models.BooleanField(default=False)

    class Meta:
        model = models.Donation
        fields = ['datetime_of_donation', 'donor', 'currency_type', 'notified', 'amount', 'section18a_issued']
