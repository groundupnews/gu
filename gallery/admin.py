from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db.models import CharField, TextField

from . import models

from filebrowser.settings import ADMIN_VERSIONS, VERSIONS

class KeywordAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}

class PhotographAdmin(admin.ModelAdmin):
    fields = ('image', 'photographer', 'suggested_caption', 'alt', 'date_taken',
              'featured', 'keywords', 'albums','copyright', 'credit',)
    search_fields = ['pk', 'suggested_caption', 'keywords__name',
                     'photographer__first_names', 'photographer__last_name',
                     'albums__name',]
    ordering = ['-modified', ]
    raw_id_fields = ('photographer','keywords', 'albums',)
    autocomplete_lookup_fields = {
        'fk': ['photographer',],
        'm2m': ['keywords', 'albums',]
    }
    list_display = ('pk', 'alt', 'thumbnail', 'photographer',
                    'date_taken','created',
                    'featured', 'modified',)
    list_editable = ('featured',)

class PhotoInline(admin.TabularInline):
    search_fields = ['']
    fields = ('photograph',)
    raw_id_fields = ('photograph',)
    autocomplete_lookup_fields = {
        'fk' : ['photograph', ]
    }
    model = models.Photograph.albums.through
    ordering = ['-photograph__modified', ]
    formfield_overrides = {
        CharField: {'widget': TextInput(attrs={'size':'500'})},
        TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }


class AlbumAdmin(admin.ModelAdmin):
    search_fields = ['pk', 'name', 'description', ]
    list_display = ['pk', 'name', 'description',]
    inlines = [PhotoInline,]

admin.site.register(models.Album, AlbumAdmin)
admin.site.register(models.Photograph, PhotographAdmin)
admin.site.register(models.Keyword, KeywordAdmin)
