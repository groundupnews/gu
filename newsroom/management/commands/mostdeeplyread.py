from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import json
import datetime
from urllib.request import urlopen
from urllib.parse import urlencode, urlparse

from newsroom.models import Article
from newsroom.models import MostDeeplyRead


def get_most_visited_pages():
    key = settings.PIWIK_TOKEN_AUTH
    num_entries = 100 
    site_id = settings.PIWIK_SITEID
    prefix = settings.PIWIK_SITE_URL
    url_dict = {
        "module": "API",
        "token_auth": key,
        "method": "Actions.getPageUrls",
        "flat": "1",
        "filter_limit": str(num_entries),
        "filter_sort_column": "nb_uniq_visitors", 
        "idSite": str(site_id),
        "date": "today",
        "period": "week",
        "format": "json"
    }
    query = urlencode(url_dict)
    response = urlopen(prefix + "?" + query)
    data = response.read().decode('utf-8')
    return json.loads(data)


def get_most_deeply_read(num_articles):
    results = get_most_visited_pages()
    candidate_articles = []
    
    for result in results:
        if not ("url" in result):
            continue
        try:
            avg_time = float(result.get("avg_time_on_page", 0))
        except (ValueError, TypeError):
            avg_time = 0.0
            
        path = urlparse(result["url"].replace("\\", "")).path
        if path[0:9].strip() == "/article/":
            slug = path[9:-1]
            try:
                article = Article.objects.get(slug=slug)
                if not article.is_published():
                    continue
                # recent -- last 7 days
                if article.published >= timezone.now() - datetime.timedelta(days=7):
                    candidate_articles.append({
                        'article': article,
                        'avg_time': avg_time
                    })
            except ObjectDoesNotExist:
                continue

    # sort avg_time DESC
    candidate_articles.sort(key=lambda x: x['avg_time'], reverse=True)
    
    final_list = []
    # avoids duplicates if any!
    seen_slugs = set()
    
    for item in candidate_articles:
        if len(final_list) >= num_articles:
            break
        slug = item['article'].slug
        if slug not in seen_slugs:
            final_list.append(slug + "|" + item['article'].title)
            seen_slugs.add(slug)
        
    mostdeeplyread = MostDeeplyRead()
    mostdeeplyread.article_list = "\n".join(final_list)
    mostdeeplyread.save()


class Command(BaseCommand):
    help = 'Get the most deeply read GroundUp articles from Piwik'

    def add_arguments(self, parser):
        parser.add_argument('numarticles', type=int,
                            help="Number of articles to include")

    def handle(self, *args, **options):
        num_articles = options["numarticles"]
        print("MostDeeplyRead: {0}: Processing 1 week for {1} articles.".format(
            str(timezone.now()), num_articles))
        get_most_deeply_read(num_articles)
