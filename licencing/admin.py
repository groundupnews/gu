from django.contrib import admin
from . import models

# Register your models here.


class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "licensee",
        "date_from",
        "date_to",
    )


admin.site.register(models.Licence)
admin.site.register(models.Licensee)
admin.site.register(models.Contract, ContractAdmin)
