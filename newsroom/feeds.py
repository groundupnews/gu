from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse
from .models  import Article

class LatestArticlesRssFeed(Feed):
    title = "GroundUp RSS Feed"
    link = "/feeds/"
    description = "News, analysis and opinion published by GroundUp."

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

class LatestArticlesAtomFeed(LatestArticlesRssFeed):
    title = "GroundUp Atom Feed"
    feed_type = Atom1Feed
    subtitle = LatestArticlesRssFeed.description

    def item_copyright(self, article):
        return article.copyright
