from django.contrib import admin

from . import models


# Commissions

class CommissionInline(admin.StackedInline):
    model = models.Commission
    classes = ('grp-closed',)
    extra = 0

class InvoiceInline(admin.StackedInline):
    model = models.Invoice
    classes = ('grp-closed',)
    extra = 0

class ApprovedCommissionListFilter(admin.SimpleListFilter):
    title = 'Funded vs unfunded'
    parameter_name = 'approved'

    def lookups(self, request, model_admin):
        return (
            ('approved', 'Funded Commissions'),
            ('unapproved', 'Unfunded Commissions'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'unapproved':
            return queryset.filter(fund__isnull = True)
        if self.value() == 'approved':
            return queryset.filter(fund__isnull = False)

class InvoiceStatusListFilter(admin.SimpleListFilter):
    title = 'Invoice status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return models.INVOICE_STATUS_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(invoice__status = self.value())



class CommissionAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'article',
                    'commission_due', 'taxable','fund')
    list_editable = ('fund', 'commission_due', 'taxable',)
    search_fields = ('invoice__author__first_names',
                     'invoice__author__last_name',)
    list_filter = ['invoice__author', ApprovedCommissionListFilter, \
                   InvoiceStatusListFilter]
    ordering = ['-modified', ]
    raw_id_fields = ('invoice', 'article', )
    autocomplete_lookup_fields = {
        'fk': ['invoice', 'article',],
    }

class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ('author__first_names',
                     'author__last_name',)
    list_display = ('__str__', 'author', 'status', 'invoice_num',)
    inlines = [CommissionInline,]

class FundAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'description', 'bank_account',
                    'prefix', 'next_number', 'ledger',
                    'deprecated')
    list_editable = ('name', 'description', 'bank_account',
                     'prefix', 'next_number', 'ledger',
                    'deprecated')
    search_fields = ('name', 'description',)
    list_filter = ('deprecated', 'ledger',)
    ordering = ['name']

class PayeRequisitionAdmin(admin.ModelAdmin):
    search_fields = ('payee__first_names', 'payee__last_name', )
    list_display = ('pk', 'payee', 'date_from', 'date_to', 'created', 'modified', )

admin.site.register(models.RateCard)
admin.site.register(models.Fund, FundAdmin)
admin.site.register(models.Commission, CommissionAdmin)
admin.site.register(models.Invoice, InvoiceAdmin)
admin.site.register(models.PayeRequisition, PayeRequisitionAdmin)
