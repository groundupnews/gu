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


class UnprocessedListFilter(admin.SimpleListFilter):
    title = 'Approved'
    parameter_name = 'approved'

    def lookups(self, request, model_admin):
        return (
            ('unapproved', 'unapproved'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'unapproved':
            return queryset.filter(fund__isnull = True)

class CommissionAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'article',
                    'commission_due', 'taxable','fund')
    list_editable = ('fund', 'commission_due', 'taxable',)
    search_fields = ('invoice__author__first_names',
                     'invoice__author__last_name',)
    list_filter = ['invoice__author', UnprocessedListFilter,]
    ordering = ['-modified', ]
    raw_id_fields = ('invoice', 'article', )
    autocomplete_lookup_fields = {
        'fk': ['invoice', 'article',],
    }

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('author', 'status', 'invoice_num',)
    inlines = [CommissionInline,]

admin.site.register(models.Fund)
admin.site.register(models.Commission, CommissionAdmin)
admin.site.register(models.Invoice, InvoiceAdmin)
