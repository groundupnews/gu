from decimal import Decimal
import logging

from django.urls import reverse
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.utils.timezone import make_aware
from django.db import transaction

from filebrowser.fields import FileBrowseField
from newsroom.models import Article, Author, LEVEL_CHOICES
from newsroom import utils

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
    ("Administration", "Administration"),
    ("Article author", "Article author"),
    ("Article cancellation fee", "Article cancellation fee"),
    ("Consulting", "Consulting"),
    ("Expenses", "Expenses"),
    ("Editing", "Editing"),
    ("Fact check", "Fact check"),
    ("Photographs", "Photographs"),
    ("Subediting", "Subediting"),
    ("Sundry", "Sundry"),
)

RATES = {
    'primary_photo': 300.0,
    'inside_photo': 150.0,
    'opinion': 0.0,
    'brief': 324.0,
    'law': 918.0,
    'news': 918.0,
    'video': 1620.0,
    'science': 1620.0,
    'simple_feature': 1620.0,
    'complex_feature': 2376.0
}

BONUSES = [  0,   0,   0,   0,   500, 500, 500, 500, 500, 500,
             500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
             500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
             500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
             500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
             500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
             500, 500, 500, 500, 500, 500, 500, 500, 500, 500 ]

LEVELS = {
    'intern': 0.5,
    'standard': 1,
    'senior': 1.35,
    'experienced': 1.7,
    'exceptional': 2.2
}

logger = logging.getLogger("groundup")

class Fund(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=100, blank=True)
    bank_account = models.CharField(max_length=20, blank=True)
    prefix = models.CharField(max_length=5, blank=True)
    next_number = models.IntegerField(default=1)
    ledger = models.BooleanField(default=False, verbose_name="pastel")
    deprecated = models.BooleanField(default=False)

    def __str__(self):
        return self.name.upper()

    @staticmethod
    def get_funds():
        funds = [(fund.pk, fund.name) for fund in Fund.objects.all()]
        return funds

    @staticmethod
    def get_ledger_funds():
        funds = [(fund.pk, fund.name) for fund in Fund.objects.
                 filter(ledger=True).filter(deprecated=False)]
        return funds

    @staticmethod
    def get_account_funds():
        funds = [(fund.pk, fund.name) for fund in Fund.objects.
                 filter(ledger=False).filter(deprecated=False)]
        return funds


    class Meta:
        ordering = ['name', ]


EXTENSIONS = [".jpg", ".pdf", ".doc", ".docx", ".odt", ".xls", ".xlsx",
              ".zip", ".JPG", ".PDF", ".DOC", ".DOCX"]


def set_corresponding_vals(fromobj, to):
    to.invoicing_company = fromobj.invoicing_company
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
    to.level = fromobj.level

class RateCard(models.Model):
    date_from = models.DateTimeField()
    primary_photo = models.FloatField(default=0.0)
    inside_photo = models.FloatField(default=0.0)
    opinion = models.FloatField(default=0.0)
    brief = models.FloatField(default=0.0)
    law = models.FloatField(default=0.0)
    news = models.FloatField(default=0.0)
    video = models.FloatField(default=0.0)
    science = models.FloatField(default=0.0)
    simple_feature = models.FloatField(default=0.0)
    complex_feature = models.FloatField(default=0.0)
    bonus = models.FloatField(default=0.0)
    bonus_article = models.PositiveSmallIntegerField(default=4)
    level_intern = models.FloatField(default=0.5)
    level_standard = models.FloatField(default=1.0)
    level_senior = models.FloatField(default=1.35)
    level_experienced = models.FloatField(default=1.7)
    level_exceptional = models.FloatField(default=2.2)

    def __str__(self):
        return str(self.date_from)

    @staticmethod
    def get_current_record():
        try:
            return RateCard.objects.filter(date_from__lte=timezone.now()).\
                latest('date_from')
        except:
            return None

    @staticmethod
    def populate_rates():
        ratecard = RateCard.get_current_record()
        if ratecard:
            RATES['primary_photo'] = ratecard.primary_photo
            RATES['inside_photo'] = ratecard.inside_photo
            RATES['opinion'] = ratecard.opinion
            RATES['brief'] = ratecard.brief
            RATES['law'] = ratecard.law
            RATES['news'] = ratecard.news
            RATES['video'] = ratecard.video
            RATES['science'] = ratecard.science
            RATES['simple_feature'] = ratecard.simple_feature
            RATES['complex_feature'] = ratecard.complex_feature

            BONUSES = ratecard.bonus_article * [0] + 50 * [ratecard.bonus]
            LEVELS['intern'] =  ratecard.level_intern
            LEVELS['standard'] = ratecard.level_standard
            LEVELS['senior'] = ratecard.level_senior
            LEVELS['experienced'] = ratecard.level_experienced
            LEVELS['exceptional'] = ratecard.level_exceptional

    class Meta:
        ordering = ["-date_from", ]


class Invoice(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    invoice_num = models.IntegerField(default=0)

    # Fields whose default values are taken from Author
    identification = models.CharField(max_length=20, blank=True,
                                      help_text="SA ID, passport or some form "
                                      "of official identification")
    dob = models.DateField(blank=True, null=True, verbose_name="date of birth",
                           help_text="Required by SARS")
    invoicing_company = models.CharField(
        blank=True, max_length=100,
        help_text="Leave blank unless you invoice through a company")
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
                              help_text="If you are VAT registered "
                              "set this to 15 else leave at 0")
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES,
                             default='standard')
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
    additional_emails = models.CharField(max_length=200, blank=True,
                                         help_text="Additional emails to notify "
                                         "separated by commas")
    date_time_reporter_approved = models.DateTimeField(null=True, blank=True,
                                                       editable=False)
    date_time_editor_approved = models.DateTimeField(null=True, blank=True,
                                                     editable=False)
    date_time_processed = models.DateTimeField(null=True, blank=True,
                                               editable=False)
    date_notified_payment = models.DateTimeField(null=True, blank=True,
                                                 editable=False)

    # Requisition print fields
    requisition = models.BooleanField(default=False)
    requisition_number = models.CharField(blank=True, max_length=12)
    payment_method = models.CharField(blank=True, default="EFT", max_length=12)
    description = models.CharField(blank=True, max_length=200)
    fund = models.ForeignKey(Fund, blank=True, null=True,
                             on_delete=models.CASCADE)
    vouchers_attached = models.BooleanField(default=True)
    prepared_by = models.CharField(max_length=100, blank=True)
    approved_by = models.CharField(max_length=100, blank=True)
    authorised_by = models.CharField(max_length=100, blank=True)

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

    def quick_calc_payment(self):
        if self.status >= "4":
            return (self.amount_paid, self.vat_paid,
                    self.tax_paid, self.amount_paid - self.vat_paid + self.tax_paid)
        else:
            return self.calc_payment()

    def __str__(self):
        return str(self.author.pk) + "-" + str(self.invoice_num) + " - " + \
            str(self.author) + " - " + self.get_status_display()

    def get_absolute_url(self):
        return reverse('payments:invoice.detail', args=[self.author.pk,
                                                        self.invoice_num])

    def short_string(self):
        return str(self.author.pk) + "-" + str(self.invoice_num)

    def process_splits(self):
        commissions = self.commission_set.filter(split=True)
        if len(commissions) > 0:
            new_invoice = Invoice.create_invoice(self.author)
            for commission in commissions:
                commission.split = False
                commission.invoice = new_invoice
                commission.save()

    def accepted_commissions(self):
        return self.commission_set.filter(fund__isnull=False).filter(deleted=False)

    def save(self, *args, **kwargs):
        try:
            with transaction.atomic():
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
                self.process_splits()
        except Exception as e:
            msg = "Error saving invoice: " + str(e)
            messages.add_message(request, messages.ERROR, msg)
            print(msg)
            logger.error(msg)

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

    @staticmethod
    def merge_invoices(from_invoice, to_invoice):
        for commission in from_invoice.commission_set.all():
            commission.invoice = to_invoice
            commission.save()
            from_invoice.status = "5"
        from_invoice.save()

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
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, blank=True, null=True,
                                on_delete=models.CASCADE)
    description = models.CharField(max_length=50, blank=True,
                                   verbose_name="secondary description",
                                   default="Article author",
                                   choices=COMMISSION_DESCRIPTION_CHOICES)
    notes = models.CharField(max_length=200, blank=True)
    fund = models.ForeignKey(Fund, blank=True, null=True,
                             verbose_name="ledger",
                             on_delete=models.CASCADE,
                             help_text="Selecting a Pastel ledger account "
                             "approves the commission")
    sys_generated = models.BooleanField(default=False)
    date_generated = models.DateTimeField(blank=True, null=True)
    date_approved = models.DateField(blank=True, null=True)
    date_notified_approved = models.DateTimeField(blank=True, null=True)
    commission_due = models.DecimalField(max_digits=7,
                                         decimal_places=2, default=0.00,
                                         verbose_name="amount")
    taxable = models.BooleanField(default=True)
    vatable = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)
    split = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    objects = CommissionQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('payments:invoice.detail',
                       args=[self.invoice.author.pk, self.invoice.invoice_num])

    def save(self, *args, **kwargs):
        if self.fund is not None and self.date_approved is None:
            self.date_approved = timezone.now()
        super(Commission, self).save(*args, **kwargs)


    def estimate_bonus(self):
        if self.article and self.article.is_published() \
           and self.article.author_01 == self.invoice.author \
           and self.invoice.author.freelancer == "f":
            month_start = make_aware(timezone.datetime(self.article.published.year,
                                            self.article.published.month, 1))
            publish_time = self.article.published
            published_this_month = Article.objects.published().\
                                   filter(published__gte=month_start).\
                                   filter(published__lt=publish_time).\
                                   filter(author_01=self.invoice.author).count() + 1
            return BONUSES[published_this_month]
        else:
            return 0.00

    def estimate_payment_st(self, estimate):
        RateCard.populate_rates()
        try:
            experience = LEVELS[self.invoice.author.level]
        except:
            experience = 1.0

        estimate['experience'] = experience

        if self.article.author_01 is None:
            shared = 1.0
        elif self.article.author_02 is None:
            shared = 1.0
        elif self.article.author_03 is None:
            shared = 2.0
        elif self.article.author_04 is None:
            shared = 3.0
        elif self.article.author_05 is None:
            shared = 4.0
        else:
            shared = 5.0

        estimate['shared'] = shared

        category_name = self.article.category.name.lower()
        if category_name in RATES:
            article = RATES[category_name]
        else:
            article = RATES["news"]


        if category_name == "feature":
            if len(self.article.body.split(" ")) > 850:
                article = RATES["complex_feature"]
            else:
                article = RATES["simple_feature"]

        estimate['article'] = article

        inside_primary_image = 0
        primary_photo = 0.0

        if self.article.primary_image and \
           (str(self.invoice.author).lower() in
            self.article.primary_image_caption.lower()):
            primary_photo = RATES['primary_photo']
        elif not self.article.primary_image:
            caption = utils.get_first_caption(self.article.body)
            if caption:
                inside_primary_image = 1
                if str(self.invoice.author).lower() in caption.lower():
                    primary_photo = RATES['primary_photo']

        estimate['primary_photo'] = primary_photo

        num_images = self.article.body.count("<img ") - inside_primary_image - \
            self.article.body.count('id="gu_counter"') - \
            self.article.body.count("id='gu_counter'")
        estimate['inside_photos'] = num_images * RATES["inside_photo"]
        estimate['bonus'] = self.estimate_bonus()

        return estimate

    def estimate_payment_writer(self, estimate):
        try:
            experience = LEVELS[self.invoice.author.level]
        except:
            experience = 1.0

        estimate['experience'] = experience

        if self.article.category.name == "Brief":
            article = RATES["brief"]
        elif self.article.category.name == "Feature":
            article = RATES["complex_feature"]
        elif self.article.category.name == "Opinion":
            article = RATES["opinion"]
        else:
            article = RATES["news"]

        estimate['article'] = article
        estimate['bonus'] = self.estimate_bonus()

        return estimate

    def estimate_payment_photographer(self, estimate):
        estimate['primary_photo'] = RATES['primary_photo']
        num_images = self.article.body.count("<img ")
        estimate['inside_photos'] = num_images * RATES["inside_photo"]
        return estimate

    def estimate_payment_tp(self, estimate):
        estimate['shared'] = 1
        if not (self.article.author_01 and self.article.author_02):
            return estimate
        if self.invoice.author == self.article.author_01:
            return self.estimate_payment_writer(estimate)
        elif self.invoice.author == self.article.author_02:
            return self.estimate_payment_photographer(estimate)
        else:
            return estimate

    def estimate_payment(self):
        estimate = {
            'article': 0.0,
            'experience': 0.00,
            'primary_photo': 0.00,
            'inside_photos': 0.00,
            'shared': 1.00,
            'bonus': 0.00,
            'total': 0.00
        }

        # This code is not so important that it should ever crash the site
        try:
            if self.article and self.description == "Article author":

                if self.article.author_01 == self.invoice.author or \
                   self.article.author_02 == self.invoice.author or \
                   self.article.author_03 == self.invoice.author or \
                   self.article.author_04 == self.invoice.author or \
                   self.article.author_05 == self.invoice.author:

                    if self.article.byline_style == "ST":
                        estimate = self.estimate_payment_st(estimate)
                    elif self.article.byline_style == "TP":
                        estimate = self.estimate_payment_tp(estimate)
        except Exception as e:
            logger.warning("Error calculating payment: " + str(e))

        estimate['total'] = (estimate['article'] * estimate['experience'] +
                             estimate['primary_photo'] +
                             estimate['inside_photos']) / estimate['shared'] + \
                             estimate['bonus']
        return estimate

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
