from ajax_select.fields import AutoCompleteSelectMultipleField
from django import forms
from . import models

class TweetForm(forms.ModelForm):
    tag_accounts = AutoCompleteSelectMultipleField("twitterhandles", required=False, label="Tweeters")

    class Meta:
        model = models.Tweet
        fields = ['tweet_text', 'status', 'tag_accounts', ]
