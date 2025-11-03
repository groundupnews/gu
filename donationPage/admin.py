from django.contrib import admin

from .models import Donor, Currency, Donation, Subscription


class DonorAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "display_name", "email")
    list_editable = ("name", "display_name", "email")
    search_fields = ("name", "display_name", "email")


# repeat for other models.
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "donor",
        "datetime_of_donation",
        "currency_type",
        "amount",
        "notified",
        "section18a_issued",
    )
    search_fields = [
        "donor__name",
        "donor__email",
        "donor__pk",
    ]
    # list_editable = ('donor', 'datetime_of_donation',
    #               'currency_type', 'amount','notified','section18a_issued',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("donor", "status", "amount")
    search_fields = [
        "donor__name",
        "donor__email",
        "donor__pk",
    ]


admin.site.register(Donor, DonorAdmin)
admin.site.register(Currency)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Donation, DonationAdmin)
