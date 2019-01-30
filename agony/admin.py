from django.contrib import admin
from django import forms

from agony.models import QandA

class QandAAdmin(admin.ModelAdmin):
    list_display = ['summary_question', 'sender_name', 'sender_email',
                    'published', 'created', 'modified',
                    'notify_sender', 'sender_notified', ]
    list_editable = ['notify_sender', 'sender_notified']
    list_filter = ['published', 'topics',]
    raw_id_fields = ('topics', )
    date_hierarchy = 'published'
    search_fields = ['summary_question', 'summary_answer', 'sender_name', 'sender_email',]
    readonly_fields = ('created', 'modified', )
    autocomplete_lookup_fields = {
        'm2m': ['topics', ],
    }
    fieldsets = (
        ('Main', {
            'classes': ('wide',),
            'fields': ('summary_question', 'full_question',
                       'summary_answer', 'full_answer',
                       ('sender_name', 'sender_email', ),
                       ('notify_sender', 'sender_notified',),
                       'topics',
                       'published','notes',),
        }),
        ('Advanced', {
            'classes': ('wide',),
            'fields': ('original_question', 'answer_for_sender',
                       'created', 'modified', )
        })
    )

admin.site.register(QandA, QandAAdmin)
