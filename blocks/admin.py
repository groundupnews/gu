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
            'fields': ('name', 'block_type', )
        }),
        ('Dynamic Content Configuration', {
            'classes': ('grp-collapse', 'grp-closed'),
            'fields': ('selected_topic', 'selected_category', 'num_articles', 'feature_first_article'),
            'description': 'Select Topic OR Category, and number of articles. This will overwrite the HTML field.'
        }),
        ('HTML Content', {
            'fields': ('html',)
        }),
    )

    autocomplete_lookup_fields = {
        'fk': ['selected_topic', 'selected_category'],
    }
    raw_id_fields = ('selected_topic', 'selected_category')

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'block_list', 'modified', )
    ordering = ['-modified',]
    search_fields = ['name', 'blocks',]
    fields = ('name',)
    inlines = [BlockGroupInline,]

admin.site.register(models.Block, BlockAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.BlockGroup)
