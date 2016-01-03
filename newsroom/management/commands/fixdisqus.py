from django.core.management.base import BaseCommand, CommandError
from newsroom.models import Article

def process(start, finish):
    articles = Article.objects.all()
    for article in articles[start:finish]:
        slug_p = article.slug.rpartition("_")
        try:
            id = int(slug_p[2])
            article.disqus_id = "node/" + slug_p[2]
            print(article.disqus_id)
            article.save()
        except:
            pass

class Command(BaseCommand):
    help = 'Hack to fix disqus ids for articles imported from Drupal'

    def add_arguments(self, parser):
        parser.add_argument('start', type=int)
        parser.add_argument('finish', type=int)

    def handle(self, *args, **options):
        start = options["start"]
        finish = options["finish"]
        print("Processing with", start, finish)
        process(start, finish)
