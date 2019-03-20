from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField
from django import forms
from django.forms import Form, ModelForm
from django.contrib import messages
from newsroom.models import Article, Author
from payment.models import Commission, Invoice, Fund, COMMISSION_DESCRIPTION_CHOICES

BIRTH_YEAR_CHOICES = range(1920,2016)
COMMISSION_YEAR_CHOICES = range(2012,2050)

class InvoiceStaffForm(ModelForm):
    dob = forms.DateField(widget=
                          forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES),
                          label="Date of birth",
                          required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': '4'}),
                              required=False,
                              help_text="Required by SARS")

    class Meta:
        model = Invoice
        fields = ['identification', 'dob', 'address',
                   'bank_name', 'bank_account_number',
                   'bank_account_type', 'bank_branch_name', 'bank_branch_code',
                   'swift_code', 'iban', 'tax_no', 'tax_percent', 'vat',
                   'level', 'query',
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
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': '4'}),
                              required=True,
                              help_text="Required by SARS")

    bank_name = forms.CharField(max_length=20, required=True)
    bank_account_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = Invoice
        fields = ['identification', 'dob', 'address',
                   'bank_name', 'bank_account_number',
                   'bank_account_type', 'bank_branch_name', 'bank_branch_code',
                   'swift_code', 'iban', 'tax_no', 'tax_percent', 'vat',
                   'query',
        ]


    def clean(self):
        cleaned_data = super(InvoiceForm, self).clean()
        query = cleaned_data.get("query")
        if "query_button" in self.data and query == "":
            self.add_error("query",
                           "Please explain why you're querying "
                           "the invoice")



class CommissionForm(ModelForm):
    author = AutoCompleteSelectField("authors", required=False,
                                     help_text=None, label="Payee")
    article = AutoCompleteSelectField('articles', required=False,
                                      help_text=None)

    def clean_author(self):
        data = self.cleaned_data['author']
        if data is None:
            raise forms.ValidationError("Please enter a user")
        return data

    class Meta:
        model = Commission
        fields = ['author', 'article', 'description', 'notes',
                  'commission_due', 'taxable', 'vatable', 'fund', ]


class CommissionFormset(ModelForm):

    def clean_fund(self):
        fund = self.cleaned_data['fund']
        if 'commission_due' in self.cleaned_data:
            due = self.cleaned_data['commission_due']
        else:
            due = None
        if due and due != 0.0 and  fund is None:
            raise forms.ValidationError("Please select a fund")
        return fund


class CommissionAnalysisForm(ModelForm):
    descriptions = forms.MultipleChoiceField(choices=COMMISSION_DESCRIPTION_CHOICES,
                                            help_text="You can select multiple choices "
                                            "using the ctrl button and left click.",
                                            required=False)
    funds = forms.MultipleChoiceField(choices=Fund.get_funds,
                                      help_text="You can select multiple choices "
                                            "using the ctrl button and left click.",
                                      required=False)
    date_from = forms.DateField(widget=forms.SelectDateWidget
                                (empty_label=("Year", "Month", "Day"),
                                 years=COMMISSION_YEAR_CHOICES,
                                 attrs={'class': 'date-field'}),
                                required=False)
    date_to = forms.DateField(widget=forms.SelectDateWidget
                                (empty_label=("Year", "Month", "Day"),
                                 years=COMMISSION_YEAR_CHOICES,
                                 attrs={'class': 'date-field'}),
                                required=False)
    authors = AutoCompleteSelectMultipleField('authors', required=False,
                                             help_text="Enter text to search. "
                                              "You can select multiple payees",
                                              label="Payees")

    class Meta:
        model = Commission
        fields = ['descriptions', 'funds', 'authors', 'date_from', 'date_to', ]
