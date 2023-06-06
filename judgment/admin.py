from django.contrib import admin
from . import models

class EventAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'process_status',
                    'event_type', 'email_address',
                    'event_date', 'created', 'modified',)
    list_editable = ('process_status', 'event_type', 'event_date', )
    search_fields = ('case_id', 'judges', 'email_address',)
    list_filter = ('process_status',)
    ordering = ('-modified', )


admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Court)
