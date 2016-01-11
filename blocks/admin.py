from django.contrib import admin

# Register your models here.

from . import models

class BlockGroupInline(admin.TabularInline):
    model = models.BlockGroup
    sortable_field_name = "position"
    extra = 1

class BlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'modified', )
    ordering = ['-modified',]
    search_fields = ['name', 'html',]

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'block_list', 'modified', )
    ordering = ['-modified',]
    search_fields = ['name', 'blocks',]
    fields = ('name',)
    inlines = [BlockGroupInline,]

admin.site.register(models.Block, BlockAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.BlockGroup)
