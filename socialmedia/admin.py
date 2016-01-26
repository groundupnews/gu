from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from . import models
import tagulous

admin.site.register(models.Tweet)
tagulous.admin.register(models.TwitterHandle)

class TweetForm(forms.ModelForm):
    def clean(self, *args, **kwargs):
        if models.calc_chars_left(self.cleaned_data["tweet_text"],
                                  self.cleaned_data["image"],
                                  self.cleaned_data["tag_accounts"]) < 0:
            raise ValidationError("Tweet too long.")
        super(TweetForm, self).clean(*args, **kwargs)

class TweetInline(admin.TabularInline):
    form = TweetForm
    model = models.Tweet
    readonly_fields = ('characters_left',)
    fields = ('wait_time', 'tweet_text', 'image',
              'tag_accounts',  'status', 'characters_left',)
    classes = ('grp-collapse grp-closed',)
    extra = 3

    class Media:
        js = [
            '/static/socialmedia/js/tweets.js',
        ]
