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
    ordering = ('-modified',)
    readonly_fields = ('created', 'modified', )
    autocomplete_lookup_fields = {
        'm2m': ['topics', ],
    }
    fieldsets = (
        ('', {
            'classes': ('wide',),
            'fields': (
                ('sender_name', 'sender_email', ),
                'original_question', 'answer_for_sender',
                'summary_question', 'full_question',
                'summary_answer', 'full_answer',
                ('notify_sender', 'sender_notified',),
                'topics',
                'published', 'recommended', 'notes',
                ('created', 'modified',),)
        }),
    )

    class Media:
        css = {'all': ('/static/newsroom/css/admin_enhance.css', )}
        js = [
            '//cdn.ckeditor.com/4.11.2/standard-all/ckeditor.js',
            '/static/newsroom/js/ck_styles.js',
            '/static/newsroom/js/ck_init_admin.js',
        ]


admin.site.register(QandA, QandAAdmin)
