from django.utils.text import slugify
from .models import Article
from django.utils import timezone

def create_articles(num):
    article = Article.objects.all()[0]
    pk = article.pk
    for i in range(num):
        article = Article()
        article.title = "Article number " + str(i+pk)
        article.slug = slugify(article.title)
        article.published = timezone.now()
        article.save()
