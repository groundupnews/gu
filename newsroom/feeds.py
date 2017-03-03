from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse
from .models  import Article
from django.contrib.sites.models import Site
from django.conf import settings

import os

from newsroom.settings import LOGO

class LatestArticlesRssFeed(Feed):
    title = "GroundUp News"
    link = "/feeds/"
    description = "Original news, features and opinion, mostly related to human rights, from South Africa."

    def items(self):
        return Article.objects.published()[:15]

    def item_title(self, article):
        return article.title

    def item_pubdate(self, article):
       return article.published

    def item_copyright(self, article):
        return article.copyright

    def item_description(self, article):
        return article.cached_summary_text

    def item_updateddate(self, article):
        return article.modified

    def item_enclosure_url(self, article):
        if article.primary_image:
            try:
                url = article.primary_image.version_generate("medium").url
            except:
                url = settings.STATIC_URL + LOGO
        else:
            url = settings.STATIC_URL + LOGO
        full_url = 'http://%s%s' % (Site.objects.get_current().domain, url)
        return full_url

    def item_enclosure_length(self, article):
        try:
            if article.primary_image:
                return article.primary_image.version_generate("medium").\
                    filesize
            else:
                return os.path.getsize(settings.STATIC_ROOT + LOGO)
        except:
            return os.path.getsize(settings.STATIC_ROOT + LOGO)

    def item_enclosure_mime_type(self, article):
        try:
            if article.primary_image:
                suffix = article.primary_image.version_generate("medium").\
                         url[-3:]
            else:
                suffix = LOGO[-3:]

            if suffix.lower() == "png":
                    return "image/png"
            else:
                return "image/jpeg"
        except:
            return "image/png"

class LatestArticlesAtomFeed(LatestArticlesRssFeed):
    feed_type = Atom1Feed
    subtitle = LatestArticlesRssFeed.description

    def item_copyright(self, article):
        return article.copyright
