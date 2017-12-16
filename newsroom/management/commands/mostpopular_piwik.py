from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import json
import datetime
from urllib.request import urlopen
from urllib.parse import urlencode, urlparse

from newsroom.models import Article
from newsroom.models import MostPopular


def get_most_visited_pages():
    key = settings.PIWIK_TOKEN_AUTH
    num_entries = settings.PIWIK_ENTRIES
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
    result = urlopen(prefix + "?" + query).read()
    result = str(result)[2:-1]
    return json.loads(result)


def get_most_popular_urls(num_articles):
    results = get_most_visited_pages()
    article_list = []
    num_found = 0
    for result in results:
        if num_found >= num_articles:
            break
        if not ("url" in result):
            continue
        path = urlparse(result["url"].replace("\\", "")).path
        if path[0:9].strip() == "/article/":
            slug = path[9:-1]
            try:
                article = Article.objects.get(slug=slug)
                if not article.is_published():
                    continue
                if article.published >= timezone.now() - \
                   datetime.timedelta(days=7):
                    article_list.append(article.slug + "|" + article.title)
                    num_found = num_found + 1
            except ObjectDoesNotExist:
                continue
    mostpopular = MostPopular()
    mostpopular.article_list = "\n".join(article_list)
    mostpopular.save()


class Command(BaseCommand):
    help = 'Get the most popular GroundUp articles from Piwik'

    def add_arguments(self, parser):
        parser.add_argument('numarticles', type=int,
                            help="Number of articles to include")

    def handle(self, *args, **options):
        num_articles = options["numarticles"]
        print("Mostpopular-piwik: {0}: Processing 1 week for "
              "{1} articles.".format(str(timezone.now()), num_articles))
        get_most_popular_urls(num_articles)
