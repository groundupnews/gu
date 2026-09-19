import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed
from django.utils.encoding import iri_to_uri

from newsroom.settings import LOGO
from .models import Article, Video


class LatestArticlesRssFeed(Feed):
    title = "GroundUp News"
    link = "/feeds/"
    feed_type = Rss201rev2Feed
    description = "Original news, features and opinion, "
    "mostly related to human rights, from South Africa."

    def items(self):
        return Article.objects.published()[:15]

    def item_title(self, article):
        return article.title

    def item_pubdate(self, article):
        return article.published

    def item_categories(self, article):
        return (article.category, )

    def item_copyright(self, article):
        return article.copyright

    def item_description(self, article):
        return article.cached_summary_text

    def item_author_name(self, article):
        return article.calc_byline(by_string="")

    def item_updateddate(self, article):
        return article.modified

    def item_enclosure_url(self, article):
        if article.cached_summary_image:
            try:
                url = article.cached_summary_image
            except:
                url = settings.STATIC_URL + LOGO
        else:
            url = settings.STATIC_URL + LOGO
        full_url = 'https://%s%s' % (Site.objects.get_current().domain, url)
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
            if article.cached_summary_image:
                suffix = article.cached_summary_image[-3:]
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


class LatestFullArticlesRssFeed(LatestArticlesRssFeed):
    title = "GroundUp News (full content)"
    description_template = 'newsroom/rss_feed.html'


class AtomWithContent(Atom1Feed):

    def item_attributes(self, item):
        attrs = super().item_attributes(item)
        attrs['content'] = ''
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)

        if item['content'] is not None:
            handler.addQuickElement(u'content', item['content'],
                                    {"type": "html"})

class LatestFullArticlesAtomFeed(LatestArticlesAtomFeed):
    title = "GroundUp News (full content)"
    feed_type = AtomWithContent

    def item_extra_kwargs(self, item):
        extra = super().item_extra_kwargs(item)
        extra.update({'content': self.item_content(item)})
        return extra

    def item_content(self, article):
        return article.body


class LatestVideosRssFeed(Feed):
    title = "GroundUp Videos"
    link = "/videos/"
    feed_type = Rss201rev2Feed
    description = "Video journalism from GroundUp, on our YouTube channel."

    def items(self):
        return Video.objects.list_view()[:15]

    def item_title(self, video):
        return video.title

    def item_pubdate(self, video):
        return video.published

    def item_updateddate(self, video):
        return video.modified

    def item_description(self, video):
        return video.summary

    def item_author_name(self, video):
        return video.get_byline()

    def item_categories(self, video):
        if video.category:
            return (video.category.name, )
        return ()

    def item_enclosure_url(self, video):
        return video.thumbnail_url()

    def item_enclosure_mime_type(self, video):
        return "image/jpeg"

    def item_enclosure_length(self, video):
        # Not known without fetching the thumbnail
        return 0


class LatestVideosAtomFeed(LatestVideosRssFeed):
    feed_type = Atom1Feed
    subtitle = LatestVideosRssFeed.description
