from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse
from .models  import Photograph
from django.contrib.sites.models import Site
from django.conf import settings

import os

class LatestPhotosRssFeed(Feed):
    title = "GroundUp Images"
    link = "/feeds/"
    description = "Free South African image gallery."

    def items(self):
        return Photograph.objects.order_by("-created").distinct()[:15]

    def item_title(self, photograph):
        return photograph.alt

    def item_pubdate(self, photograph):
       return photograph.created

    def item_copyright(self, photograph):
        return photograph.copyright

    def item_description(self, photograph):
        return photograph.suggested_caption

    def item_updateddate(self, photograph):
        return photograph.modified

    def item_enclosure_url(self, photograph):

        url = photograph.image.version_generate("medium").url

        full_url = 'http://%s%s' % (Site.objects.get_current().domain, url)
        return full_url

    def item_enclosure_length(self, photograph):
        return photograph.image.version_generate("medium").filesize


    def item_enclosure_mime_type(self, photograph):
        suffix = photograph.image.version_generate("medium").url[-3:]

        if suffix.lower() == "png":
            return "image/png"
        else:
            return "image/jpeg"

class LatestFeaturedPhotosRssFeed(LatestPhotosRssFeed):
    title = "GroundUp Featured Photos"
    description = "Featured photos from GroundUp's free image gallery."

    def items(self):
        return Photograph.objects.filter(featured=True).\
            order_by("-created").distinct()[:15]


class LatestPhotosAtomFeed(LatestPhotosRssFeed):
    feed_type = Atom1Feed
    subtitle = LatestPhotosRssFeed.description

class LatestFeaturedPhotosAtomFeed(LatestFeaturedPhotosRssFeed):
    feed_type = Atom1Feed
    subtitle = LatestFeaturedPhotosRssFeed.description
