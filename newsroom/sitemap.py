from django.contrib.sitemaps import Sitemap
from .models import Article, Video


class ArticleSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.8

    def items(self):
        return Article.objects.published()

    def lastmod(self, obj):
        return obj.published


class VideoSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Video.objects.published()

    def lastmod(self, obj):
        return obj.modified
