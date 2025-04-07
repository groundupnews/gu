from django.contrib import admin
from django import forms
from django.utils.translation import gettext_lazy

from agony.models import QandA

class QandAAdmin(admin.ModelAdmin):
    list_display = ['summary_question', 'sender_name', 'sender_email',
                    'published', 'created',
                    'notify_sender', 'sender_notified', 'status', ]
    list_editable = ['status', 'notify_sender', ]
    list_filter = ['status', 'published', 'topics',]
    raw_id_fields = ('topics', )
    date_hierarchy = 'published'
    search_fields = ['summary_question', 'summary_answer',
                     'sender_name', 'sender_email',]
    ordering = ('-modified',)
    readonly_fields = ('created', 'modified', 'published', 'notify_sender',
                       'sender_notified')
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
                'summary_answer', 'full_answer', 'salutation',
                ('notify_sender', 'sender_notified',),
                'topics',
                'published', 'recommended', 'notes', 'status',
                ('created', 'modified',),)
        }),
    )

    def unpublish_qandas(self, request, queryset):
        rows_updated = queryset.update(status='N', published=None)
        if rows_updated == 1:
            message_bit = "1 Q&A was"
        else:
            message_bit = "%s Q&As were" % rows_updated
        self.message_user(request, gettext_lazy("%s successfully marked as unpublished." % message_bit))

    unpublish_qandas.short_description = "Unpublish selected Questions and Answers"

    actions = [unpublish_qandas, ]

    class Media:
        css = {'all': ('/static/newsroom/css/admin_enhance.css', )}
        js = [
            '//cdn.ckeditor.com/4.11.2/standard-all/ckeditor.js',
            '/static/newsroom/js/ck_styles.js',
            '/static/newsroom/js/ck_init_admin.js',
        ]


admin.site.register(QandA, QandAAdmin)
