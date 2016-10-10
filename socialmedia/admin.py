from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from django.forms import TextInput
from . import models
from django.db import models as django_models

class TweetAdmin(admin.ModelAdmin):
    list_display = ['article', 'tweet_text', 'characters_left', 'status', ]
    list_filter = ['status', ]
    search_fields = ['article__title', 'tweet_text', ]
    ordering = ['status', 'article__modified']


class TwitterHandleAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


admin.site.register(models.Tweet, TweetAdmin)
admin.site.register(models.TwitterHandle, TwitterHandleAdmin)


class TweetForm(forms.ModelForm):
    def clean(self, *args, **kwargs):
        twitter_handles = [str(name) for name in
                           self.cleaned_data['tag_accounts']]
        if models.calc_chars_left(self.cleaned_data["tweet_text"],
                                  self.cleaned_data["image"],
                                  twitter_handles) < 0:
            raise ValidationError("Tweet too long.")
        super(TweetForm, self).clean(*args, **kwargs)


class TweetInline(admin.TabularInline):
    form = TweetForm
    model = models.Tweet
    readonly_fields = ('characters_left',)
    fields = ('wait_time', 'tweet_text', 'image',
              'tag_accounts',  'status', 'characters_left',)
    raw_id_fields = ('tag_accounts', )
    autocomplete_lookup_fields = {
        'm2m': ['tag_accounts', ],
    }
    classes = ('grp-collapse grp-closed',)
    extra = 5

    class Media:
        js = [
            '/static/socialmedia/js/tweets.js',
        ]
