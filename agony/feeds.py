from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.urls import reverse
from django.utils.html import strip_tags
from agony.models import QandA

class LatestQandARssFeed(Feed):
    title = "GroundUp Q&A"
    link = "/qanda/"
    description = "Latest questions and answers from GroundUp"
    
    def items(self):
        return QandA.objects.published().order_by('-published')[:20]
        
    def item_title(self, item):
        return item.summary_question
        
    def item_description(self, item):
        description = ""
        if item.summary_answer:
            description += "<p><strong>Short answer: </strong></p>"
            description += item.summary_answer
        if item.full_answer:
            description += "<p><strong>Full answer: </strong></p>"
            description += item.full_answer
        return description
        
    def item_link(self, item):
        return reverse('agony:detail', args=[item.pk])

    def item_pubdate(self, item):
        return item.published
        
class LatestQandAAtomFeed(LatestQandARssFeed):
    feed_type = Atom1Feed
    subtitle = LatestQandARssFeed.description
