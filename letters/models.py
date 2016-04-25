from django.db import models
from newsroom.models import Article

# Create your models here.


class Letter(models.Model):
    article = models.ForeignKey(Article)
    byline = models.CharField(max_length=200)
    email = models.EmailField()
    author_response = models.BooleanField(default=False)
    author_response_pk = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200)
    text = models.TextField(blank=True)
    rejected = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    published = models.DateTimeField(blank=True, null=True,
                                     verbose_name='publish time')
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['article', 'position', ]
