# TEMPORARILY DISABLED
# from django.contrib.syndication.views import Feed
# from django.utils.feedgenerator import Atom1Feed
# from django.urls import reverse
# from django.utils.html import strip_tags
# from agony.models import QandA
# from django.core.cache import cache

# class LatestQandARssFeed(Feed):
#     title = "GroundUp Q&A"
#     link = "/qanda/"
#     description = "Latest questions and answers from GroundUp"
    
#     def items(self):
#         cached_items = cache.get('latest_qanda_items')
#         if cached_items is not None:
#             return cached_items
#         items = QandA.objects.published()\
#             .only('summary_question', 'summary_answer', 'full_answer', 'published', 'pk')\
#             .order_by('-published')[:20]
#         cache.set('latest_qanda_items', items, 3600)  # cache for 1 hour
#         return items
        
#     def item_title(self, item):
#         return item.summary_question
        
#     def item_description(self, item):
#         description = ""
#         if item.summary_answer:
#             description += "<p><strong>Short answer: </strong></p>"
#             description += item.summary_answer
#         if item.full_answer:
#             description += "<p><strong>Full answer: </strong></p>"
#             description += item.full_answer
#         return description
        
#     def item_link(self, item):
#         return reverse('agony:detail', args=[item.pk])

#     def item_pubdate(self, item):
#         return item.published
        
# class LatestQandAAtomFeed(LatestQandARssFeed):
#     feed_type = Atom1Feed
#     subtitle = LatestQandARssFeed.description
