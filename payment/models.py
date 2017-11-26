from django.db import models
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db.models import Max
from decimal import Decimal
from filebrowser.fields import FileBrowseField

from newsroom.models import Author, Article

INVOICE_STATUS_CHOICES = (
    ("-", "Invoice being prepared by editor"),
    ("0", "Reporter needs to approve"),
    ("1", "Queried by reporter"),
    ("2", "Approved by reporter"),
    ("3", "Approved by editor"),
    ("4", "Paid"),
    ("5", "Deleted"),
)

COMMISSION_DESCRIPTION_CHOICES = (
    ("", ""),
    ("Article author", "Article author"),
    ("Photographs", "Photographs"),
    ("Article cancellation fee", "Article cancellation fee"),
    ("Expenses", "Expenses"),
    ("Editing", "Editing"),
    ("Subediting", "Subediting"),
    ("Consulting", "Consulting"),
    ("Administration", "Administration"),
    ("Sundry", "Sundry"),
)


class Fund(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name.upper()

    class Meta:
        ordering = ['name', ]


EXTENSIONS = [".jpg", ".pdf", ".doc", ".docx", ".odt", ".xls", ".xlsx",
              ".zip", ".JPG", ".PDF", ".DOC", ".DOCX"]


def set_corresponding_vals(fromobj, to):
    to.identification = fromobj.identification
    to.dob = fromobj.dob
    to.address = fromobj.address
    to.bank_name = fromobj.bank_name
    to.bank_account_number = fromobj.bank_account_number
    to.bank_branch_name = fromobj.bank_branch_name
    to.bank_branch_code = fromobj.bank_branch_code
    to.swift_code = fromobj.swift_code
    to.iban = fromobj.iban
    to.tax_no = fromobj.tax_no
    to.tax_percent = fromobj.tax_percent
    to.vat = fromobj.vat


class Invoice(models.Model):
    author = models.ForeignKey(Author)
    invoice_num = models.IntegerField(default=0)
    # Fields whose default values are taken from Author
    identification = models.CharField(max_length=20, blank=True,
                                      help_text="SA ID, passport or some form "
                                      "of official identification")
    dob = models.DateField(blank=True, null=True, verbose_name="date of birth",
                           help_text="Required by SARS")
    address = models.TextField(blank=True,
                               help_text="Required by SARS")
    bank_name = models.CharField(max_length=20, blank=True)
    bank_account_number = models.CharField(max_length=20,
                                           verbose_name="account",
                                           blank=True)
    bank_account_type = models.CharField(max_length=20,
                                         verbose_name="account type",
                                         default="CURRENT")
    bank_branch_name = models.CharField(max_length=20, blank=True,
                                        verbose_name="branch name",
                                        help_text="Unnecessary for Capitec, "
                                        "FNB, Standard, Nedbank and Absa")
    bank_branch_code = models.CharField(max_length=20, blank=True,
                                        verbose_name="branch code",
                                        help_text="Unnecessary for Capitec, "
                                        "FNB, Standard, Nedbank and Absa")
    swift_code = models.CharField(max_length=12, blank=True,
                                  help_text="Only relevant for banks "
                                  "outside SA")
    iban = models.CharField(max_length=34, blank=True,
                            help_text="Only relevant for banks outside SA")
    tax_no = models.CharField(max_length=50, blank=True,
                              verbose_name="tax number",
                              help_text="Necessary for SARS.")
    tax_percent = models.DecimalField(max_digits=2, decimal_places=0,
                                      default=25,
                                      verbose_name="PAYE %",
                                      help_text="Unless you have "
                                      "a tax directive "
                                      "we have to deduct 25% PAYE")
    vat = models.DecimalField(max_digits=2, decimal_places=0, default=0,
                              verbose_name="VAT %",
                              help_text="If you are VAT regisered "
                              "set this to 14 else leave at 0")
    ####
    # paid = models.BooleanField(default=False)
    amount_paid = models.DecimalField(max_digits=8,
                                      decimal_places=2, default=0.00,
                                      verbose_name="amount")
    tax_paid = models.DecimalField(max_digits=8,
                                   decimal_places=2, default=0.00)
    vat_paid = models.DecimalField(max_digits=8,
                                   decimal_places=2, default=0.00)
    invoice = FileBrowseField(max_length=200,
                              directory="commissions/invoices/",
                              blank=True, extensions=EXTENSIONS)
    proof = FileBrowseField(max_length=200, directory="commissions/proofs/",
                            blank=True, extensions=EXTENSIONS)
    status = models.CharField(max_length=2, choices=INVOICE_STATUS_CHOICES,
                              default="-")
    notes = models.TextField(blank=True)
    query = models.TextField(blank=True, max_length=3000,
                             help_text="Explain your query "
                             "here if you have one")
    date_time_reporter_approved = models.DateTimeField(null=True, blank=True,
                                                       editable=False)
    date_time_editor_approved = models.DateTimeField(null=True, blank=True,
                                                     editable=False)
    date_time_processed = models.DateTimeField(null=True, blank=True,
                                               editable=False)
    date_notified_payment = models.DateTimeField(null=True, blank=True,
                                                 editable=False)
    our_reference = models.CharField(max_length=20, blank=True)
    their_reference = models.CharField(max_length=20, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    def calc_payment(self):
        commissions = Commission.objects.for_authors().\
                      filter(invoice=self)
        total_uncorrected = Decimal(0.00)
        total_paid = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_vat = Decimal(0.00)
        for commission in commissions:
            (due, vat, tax, uncorrected) = commission.calc_payment()
            total_paid = total_paid + due
            total_vat = total_vat + vat
            total_tax = total_tax + tax
            total_uncorrected = total_uncorrected + uncorrected
        self.amount_paid = total_paid
        self.vat_paid = total_vat
        self.tax_paid = total_tax
        return (self.amount_paid, self.vat_paid,
                self.tax_paid, total_uncorrected,)

    def __str__(self):
        return str(self.author.pk) + "-" + str(self.invoice_num) + " - " + \
            str(self.author) + " - " + self.get_status_display()

    def get_absolute_url(self):
        return reverse('invoice.detail', args=[self.author.pk,
                                               self.invoice_num])

    def short_string(self):
        return str(self.author.pk) + "-" + str(self.invoice_num)

    def save(self, *args, **kwargs):
        if self.status == "2":  # Reporter has approved
            if self.date_time_reporter_approved is None:
                self.date_time_reporter_approved = timezone.now()
        if self.status == "3":  # Editor has approved
            if self.date_time_editor_approved is None:
                self.date_time_editor_approved = timezone.now()
        if self.status == "4":  # Invoice has been paid
            if self.date_time_processed is None:
                self.date_time_processed = timezone.now()
        self.calc_payment()
        super(Invoice, self).save(*args, **kwargs)
        set_corresponding_vals(self, self.author)
        self.author.save()

    @staticmethod
    def create_invoice(author):
        max_invoice = Invoice.objects.filter(author=author).\
                  aggregate(Max('invoice_num'))
        if max_invoice["invoice_num__max"] is None:
            invoice_num = 1
        else:
            invoice_num = max_invoice["invoice_num__max"] + 1
        invoice = Invoice()
        invoice.author = author
        invoice.invoice_num = invoice_num
        set_corresponding_vals(author, invoice)
        invoice.save()
        return invoice

    @staticmethod
    def get_open_invoice_for_author(author):
        invoices = Invoice.objects.filter(author=author).\
                                   filter(status__lte="0")
        if len(invoices) == 0:
            invoice = Invoice.create_invoice(author)
        else:
            invoice = invoices[0]
            if invoice.status == "0":
                invoice.status = "-"
                invoice.save()
        return invoice

    class Meta:
        ordering = ['status', '-modified', ]
        unique_together = ['author', 'invoice_num', ]


class CommissionQuerySet(models.QuerySet):

    def for_staff(self):
        return self.filter(deleted=False)

    def for_authors(self):
        return self.for_staff().filter(fund__isnull=False)


# Should have been named "Payment" hence the verbose_name
class Commission(models.Model):
    invoice = models.ForeignKey(Invoice)
    # The author field is now deprecated and must be removed
    # once all legacy payments are processed
    # author = models.ForeignKey(Author, blank=True, null=True)

    article = models.ForeignKey(Article, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True,
                                   default="Article author",
                                   choices=COMMISSION_DESCRIPTION_CHOICES)
    notes = models.CharField(max_length=200, blank=True)
    fund = models.ForeignKey(Fund, blank=True, null=True,
                             help_text="Selecting a fund "
                             "approves the commission")
    sys_generated = models.BooleanField(default=False)
    date_generated = models.DateTimeField(blank=True, null=True)
    date_approved = models.DateField(blank=True, null=True)
    date_notified_approved = models.DateTimeField(blank=True, null=True)
    commission_due = models.DecimalField(max_digits=7,
                                         decimal_places=2, default=0.00,
                                         verbose_name="amount")
    taxable = models.BooleanField(default=True)
    vatable = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    objects = CommissionQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('invoice.detail',
                       args=[self.invoice.author.pk, self.invoice.invoice_num])

    def save(self, *args, **kwargs):
        if self.fund is not None and self.date_approved is None:
            self.date_approved = timezone.now()
        super(Commission, self).save(*args, **kwargs)

    def calc_payment(self):
        vat = Decimal(0.00)
        if self.taxable:
            tax = (self.invoice.tax_percent / Decimal(100.00)) * \
                  self.commission_due
        else:
            tax = Decimal(0.00)
        if self.vatable:
                vat = (self.invoice.vat / Decimal(100.00)) * \
                      self.commission_due
        else:
            vat = Decimal(0.00)
        due = self.commission_due - tax + vat
        return (due, vat, tax, self.commission_due)

    def __str__(self):
        if self.invoice is not None and self.article is not None:
            return " ".join([str(self.pk), str(self.invoice.author),
                             str(self.article)])
        elif self.invoice is not None:
            return " ".join([str(self.pk), str(self.invoice.author)])
        elif self.article is not None:
            return " ".join([str(self.pk), str(self.article)])
        else:
            return str(self.pk)

    class Meta:
        ordering = ['invoice', 'created', ]
