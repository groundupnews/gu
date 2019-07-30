from datetime import timedelta

from django.shortcuts import render
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required

from .settings import LOG_FILE
from .top_urls import most_popular_pages, webpage_url_filter

# Create your views here.

@staff_member_required
def top_urls(request, minutes=10):
    cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
    urls = most_popular_pages(LOG_FILE, cutoff_time, 10,
                              webpage_url_filter)
    return render(request, "analyzer/top_urls.html",
                  {'urls': urls})
