from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db.models import CharField, TextField

from . import models

from filebrowser.settings import ADMIN_VERSIONS, VERSIONS

class KeywordAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}

class PhotographAdmin(admin.ModelAdmin):
    fields = ('image', 'photographer', 'suggested_caption', 'alt', 'date_taken',
              'featured', 'keywords', 'albums',)
    search_fields = ['suggested_caption', 'keywords', 'photographer__name',
                     'albums__name',]
    ordering = ['-modified', ]
    raw_id_fields = ('photographer','keywords', 'albums',)
    autocomplete_lookup_fields = {
        'fk': ['photographer',],
        'm2m': ['keywords', 'albums',]
    }
    list_display = ('thumbnail', 'photographer', 'date_taken','created',
                    'featured', 'modified',)
    list_display = ('featured',)

class PhotoInline(admin.TabularInline):
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
    #fields = ('name', 'description', 'photographs',)
    inlines = [PhotoInline,]


admin.site.register(models.Album, AlbumAdmin)
admin.site.register(models.Photograph, PhotographAdmin)
admin.site.register(models.Keyword, KeywordAdmin)
