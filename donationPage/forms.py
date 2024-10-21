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


class PayfastPaymentForm(DonorForm):
    # Add the payment_type field as a radio button
    PAYMENT_CHOICES = [
        ('subscription', 'Subscription'),
        ('one_time', 'One-time Payment'),
    ]

    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")
    payment_type = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Payment Type"
    )

    # Add the amount field with a default value of 100, greater than 0
    amount = forms.IntegerField(
        min_value=1,
        initial=100,
        required=True,
        label="Donation Amount (ZAR)",
        help_text="Enter amount in ZAR"
    )
    name = forms.CharField(max_length=100, required=False)
    display_name = forms.CharField(max_length=100, required=False)

    class Meta(DonorForm.Meta):
        # Include the new fields along with inherited ones
        fields = ['first_name', 'last_name', 'email', 'payment_type', 'amount']

    def clean(self):
        cleaned_data = super().clean()

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        name = ""
        # Set the name as first_name + last_name if either is provided
        if first_name or last_name:
            name = f"{first_name or ''} {last_name or ''}".strip()

        # Set the display_name to the name or fallback to email username
        if not name.strip() and email:
            email_username = email.split('@')[0]
            cleaned_data['display_name'] = email_username
            cleaned_data['name'] = email_username
        else:
            cleaned_data['display_name'] = name
            cleaned_data['name'] = name
        return cleaned_data
