from ajax_select.fields import AutoCompleteSelectField
from ajax_select.fields import AutoCompleteSelectMultipleField
from ajax_select import make_ajax_field
from django import forms
from django.forms import Form, ModelForm
from django.contrib import messages
from newsroom.models import Article, Author
from payment.models import Commission, Invoice, Fund, COMMISSION_DESCRIPTION_CHOICES
from payment.models import PayeRequisition

BIRTH_YEAR_CHOICES = range(1920,2016)
COMMISSION_YEAR_CHOICES = range(2012,2050)

class BaseInvoiceForm(ModelForm):
    dob = forms.DateField(widget=
                          forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES, attrs={"type": "date"}),
                          label="Date of birth",
                          required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': '4'}),
                              required=False,
                              help_text="Required by SARS")


class InvoiceStaffForm(BaseInvoiceForm):
    fund = forms.ModelChoiceField(queryset=Fund.objects.filter(ledger=False).
                                filter(deprecated=False),
                                required=False)
    merge = forms.ChoiceField(required=False)


    class Meta:
        model = Invoice
        fields = ['identification', 'dob', 'invoicing_company', 'address',
                  'bank_name', 'bank_account_number',
                  'bank_account_type', 'bank_branch_name', 'bank_branch_code',
                  'swift_code', 'iban', 'tax_no', 'tax_percent', 'vat',
                  'level', 'transport_claim', 'query', 'additional_emails',
                  'requisition', 'requisition_number', 'payment_method',
                  'description', 'fund', 'vouchers_attached',
                  'prepared_by', 'approved_by', 'authorised_by', 'merge',]

        widgets = {
            'transport_claim': forms.Textarea(attrs={'rows': 5}),
            'query': forms.Textarea(attrs={'rows': 5}),
        }

class InvoiceForm(BaseInvoiceForm):
    identification = forms.CharField(max_length=20, required=True,
                                     help_text=
                                     "SA ID, passport or some form "
                                     "of official identification")
    dob = forms.DateField(widget=
                          forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES, attrs={'type': 'date'}),
                          label="Date of birth",
                          required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': '4'}),
                              required=True,
                              help_text="Required by SARS")

    bank_name = forms.CharField(max_length=20, required=True)
    bank_account_number = forms.CharField(max_length=20, required=True)


    class Meta:
        model = Invoice
        fields = ['identification', 'dob', 'invoicing_company', 'address',
                   'bank_name', 'bank_account_number',
                   'bank_account_type', 'bank_branch_name', 'bank_branch_code',
                   'swift_code', 'iban', 'tax_no', 'tax_percent', 'vat',
                   'transport_claim', 'query',
        ]
        widgets = {
            'transport_claim': forms.Textarea(attrs={'rows': 5}),
            'query': forms.Textarea(attrs={'rows': 5}),
        }


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
    fund = forms.ModelChoiceField(
        queryset=Fund.objects.filter(ledger=True).filter(deprecated=False),
        label='Pastel', required=False)

    def clean_author(self):
        data = self.cleaned_data['author']
        if data is None:
            raise forms.ValidationError("Please enter a user")
        return data

    class Meta:
        model = Commission
        fields = ['author', 'article', 'fund', 'description', 'notes',
                  'commission_due', 'taxable', 'vatable', 'vat_amount' ]


class CommissionFormset(ModelForm):
    fund = forms.ModelChoiceField(
        # queryset=Fund.objects.filter(ledger=True).filter(deprecated=False),
        queryset=Fund.objects.filter(deprecated=False),
        label='Ledger', required=False)

    def clean_fund(self):
        fund = self.cleaned_data['fund']
        if 'commission_due' in self.cleaned_data:
            due = self.cleaned_data['commission_due']
        else:
            due = None
        if due and due != 0.0 and fund is None:
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
                                 attrs={'class': 'date_field', 'type': 'date'}),
                                required=False)
    date_to = forms.DateField(widget=forms.SelectDateWidget
                                (empty_label=("Year", "Month", "Day"),
                                 years=COMMISSION_YEAR_CHOICES,
                                 attrs={'class': 'date_field', 'type': 'date'}),
                                required=False)
    authors = AutoCompleteSelectMultipleField('authors', required=False,
                                             help_text="Enter text to search. "
                                              "You can select multiple payees",
                                              label="Payees")

    class Meta:
        model = Commission
        fields = ['descriptions', 'funds', 'authors', 'date_from', 'date_to', ]


class PayeRequisitionForm(ModelForm):

    def generate_invoices(self):
        PayeRequisition.generate_invoices(self.cleaned_data['payee'],
                                          self.cleaned_data['date_from'],
                                          self.cleaned_data['date_to'])

    class Meta:
        model = PayeRequisition
        fields = ['payee', 'date_from', 'date_to', ]
