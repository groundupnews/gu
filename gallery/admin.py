from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db.models import CharField, TextField
from django import forms

from . import models


class KeywordAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class DuplicateInline(admin.TabularInline):
    model = models.Duplicate


class PhotographChangelistForm(forms.ModelForm):
    suggested_caption = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "cols": 140,
                "style": "min-width: 450px",
            }
        ),
    )
    alt = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"style": "width:280px;"}),
    )

    class Meta:
        model = models.Photograph
        fields = "__all__"


class PhotographAdmin(admin.ModelAdmin):
    fields = (
        "image",
        "photographer",
        "alt",
        "suggested_caption",
        "date_taken",
        "featured",
        "slider_position",
        "keywords",
        "albums",
        "copyright",
        "credit",
        ("featured_on_front_page_from", "featured_on_front_page_to"),
        ("include_short_title", "include_suggested_caption"),
    )
    search_fields = [
        "pk",
        "suggested_caption",
        "alt",
        "keywords__name",
        "photographer__first_names",
        "photographer__last_name",
        "albums__name",
    ]
    ordering = [
        "-modified",
    ]
    raw_id_fields = (
        "photographer",
        "keywords",
        "albums",
    )
    autocomplete_lookup_fields = {
        "fk": [
            "photographer",
        ],
        "m2m": [
            "keywords",
            "albums",
        ],
    }
    list_display = (
        "id",
        "alt",
        "suggested_caption",
        "thumbnail",
        "photographer",
        "date_taken",
        "created",
        "featured",
        "modified",
    )
    list_editable = (
        "alt",
        "suggested_caption",
        "featured",
    )
    inlines = [
        DuplicateInline,
    ]

    def get_changelist_form(self, request, **kwargs):
        return PhotographChangelistForm


class PhotoInline(admin.TabularInline):
    search_fields = [""]
    fields = ("photograph",)
    raw_id_fields = ("photograph",)
    autocomplete_lookup_fields = {
        "fk": [
            "photograph__id",
        ]
    }
    model = models.Photograph.albums.through
    ordering = [
        "-photograph__id",
    ]
    formfield_overrides = {
        CharField: {"widget": TextInput(attrs={"size": "500"})},
        TextField: {"widget": Textarea(attrs={"rows": 4, "cols": 40})},
    }


class AlbumAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "description",
    ]
    list_display = [
        "pk",
        "name",
        "description",
    ]
    inlines = [
        PhotoInline,
    ]


admin.site.register(models.Album, AlbumAdmin)
admin.site.register(models.Photograph, PhotographAdmin)
admin.site.register(models.Keyword, KeywordAdmin)
