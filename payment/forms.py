from django import forms
from django.forms import ModelForm
from payment.models import Invoice

BIRTH_YEAR_CHOICES = range(1920,2016)

class InvoiceStaffForm(ModelForm):
    dob = forms.DateField(widget=
                          forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES),
                          label="Date of birth",
                          required=False)
    class Meta:
        model = Invoice
        fields = ['identification', 'dob',
                   'bank_name', 'bank_account_number',
                   'bank_account_type', 'bank_branch_name', 'bank_branch_code',
                   'swift_code', 'iban', 'tax_no', 'tax_percent', 'vat',
                   'query',
        ]


class InvoiceForm(InvoiceStaffForm):
    identification = forms.CharField(max_length=20, required=True,
                                     help_text=
                                     "SA ID, passport or some form "
                                     "of official identification")
    dob = forms.DateField(widget=
                          forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES),
                          label="Date of birth",
                          required=True)
    bank_name = forms.CharField(max_length=20, required=True)
    bank_account_number = forms.CharField(max_length=20, required=True)

    def clean(self):
        cleaned_data = super(InvoiceForm, self).clean()
        query = cleaned_data.get("query")
        if "query_button" in self.data and query == "":
            self.add_error("query",
                           "Please explain why you're querying "
                           "the invoice")

    # class Meta:
    #     model = Invoice
    #     fields = ['identification', 'dob',
    #                'bank_name', 'bank_account_number',
    #                'bank_account_type', 'bank_branch_name', 'bank_branch_code',
    #                'swift_code', 'iban', 'tax_no', 'tax_percent', 'vat',
    #                'query',
    #     ]
