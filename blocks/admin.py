from django.contrib import admin

# Register your models here.

from . import models

class BlockGroupInline(admin.TabularInline):
    model = models.BlockGroup
    sortable_field_name = "position"
    extra = 1

class BlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'block_type', 'modified', )
    # ordering = ['-modified',]
    search_fields = ['name', 'html',]
    list_filter = ('block_type',)

    fieldsets = (
        (None, {
            'fields': ('name', 'block_type', 'custom_title')
        }),
        ('Dynamic Content Source', {
            'fields': (('selected_topic', 'selected_category'),
                       ('num_articles', 'feature_first_article', 'exclude_duplicates')),
            'description': 'Select Topic OR Category, and number of articles. This will overwrite the HTML field.'
        }),
        ('Featured Article Display', {
            'classes': ('grp-collapse',),
            'fields': (('show_title_featured', 'show_summary_featured'),
                       ('show_byline_featured', 'show_date_featured', 'show_category_featured')),
        }),
        ('Standard Articles Display', {
            'classes': ('grp-collapse',),
            'fields': (('show_title_standard', 'show_summary_standard'),
                       ('show_byline_standard', 'show_date_standard', 'show_category_standard')),
        }),
        ('HTML Content', {
            'classes': ('grp-collapse',),
            'fields': ('html',)
        }),
    )

    autocomplete_lookup_fields = {
        'fk': ['selected_topic', 'selected_category'],
    }
    raw_id_fields = ('selected_topic', 'selected_category')

    class Media:
        js = ('blocks/js/block_admin.js',)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'block_list', 'modified', )
    ordering = ['-modified',]
    search_fields = ['name', 'blocks',]
    fields = ('name',)
    inlines = [BlockGroupInline,]

admin.site.register(models.Block, BlockAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.BlockGroup)
