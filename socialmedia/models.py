from django.db import models
from django.urls import reverse

from newsroom.models import Article
from filebrowser.fields import FileBrowseField
from .common import SCHEDULE_RESULTS

# Create your models here.


class TwitterHandle(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    class Meta:
        verbose_name = "Twitter handle"
        verbose_name_plural = "Twitter Handles"
        ordering = ['name', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name[0] == "@":
            self.name = self.name[1:]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('socialmedia:twitterhandle.detail', args=[self.pk, ])



def calc_chars_left(tweet_text, image, tags):
    chars_left = 210 - len(tweet_text.strip())
    if image:
        chars_left = chars_left - 24
    for account in tags:
        chars_left = chars_left - len(account.strip()) - 2
    return chars_left


class Tweet(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    wait_time = models.PositiveIntegerField(help_text="Number of minutes "
                                            "after publication "
                                            "till tweet.", default=0)
    status = models.CharField(max_length=20,
                              choices=SCHEDULE_RESULTS,
                              default="scheduled")
    tweet_text = models.CharField(max_length=200, blank=True)
    image = FileBrowseField(max_length=200, directory="images/", blank=True)
    tag_accounts = models.ManyToManyField(TwitterHandle, blank=True)
    characters_left = models.IntegerField(default=200)

    class Meta:
        ordering = ["article__published", "wait_time", ]

    def __str__(self):
        return self.article.title + ": " + str(self.wait_time)

    def save(self, *args, **kwargs):
        super(Tweet, self).save(*args, **kwargs)
        twitter_handles = [str(name) for name in self.tag_accounts.all()]
        self.characters_left = calc_chars_left(self.tweet_text,
                                               self.image,
                                               twitter_handles)
        super(Tweet, self).save(force_update=True, *args, **kwargs)
