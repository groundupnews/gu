from django.contrib.sitemaps import Sitemap
from .models import Article


class ArticleSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.8

    def items(self):
        return Article.objects.published()

    def lastmod(self, obj):
        return obj.published
