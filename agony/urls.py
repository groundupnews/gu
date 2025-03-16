from django.urls import path
from agony.views import QandAList, QandADetail
# from agony.feeds import LatestQandARssFeed, LatestQandAAtomFeed

app_name = "agony"

urlpatterns = [
    path('qanda/', QandAList.as_view(), name='list'),
    path('qanda/<int:pk>/', QandADetail.as_view(), name='detail'),
    # path('qanda/rss/', LatestQandARssFeed(), name='rss'),
    # path('qanda/atom/', LatestQandAAtomFeed(), name='atom'),
]
