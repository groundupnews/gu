from django.contrib import admin

from .models import Donor, Currency, Donation

#repeat for other models.
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'datetime_of_donation',
                    'currency_type', 'amount','notified','section18a_issued',)
    #list_editable = ('donor', 'datetime_of_donation',
     #               'currency_type', 'amount','notified','section18a_issued',)
    

admin.site.register(Donor)
admin.site.register(Currency)
admin.site.register(Donation, DonationAdmin)
