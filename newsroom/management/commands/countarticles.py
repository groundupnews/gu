from django.core.management.base import BaseCommand, CommandError
from newsroom.models import Article, Author
from django.utils import timezone
from django.db.models import Count

def process(year):
    date_from = timezone.datetime(year=year, month=1, day=1)
    date_to = timezone.datetime(year=year, month=12, day=31)
    articles = Article.objects.published().filter(published__gte=date_from). \
               filter(published__lte=date_to)
    authors = Author.objects.all()
    count = articles.values('author_01').annotate(total=Count('author_01')).\
        order_by('-total')
    result = []
    for item in count:
        pk = pk=item["author_01"]
        if pk:
            author = str(Author.objects.get(pk=item["author_01"]))
        else:
            author = "NONE"
        num = item["total"]
        result.append([author, num])
    return result


class Command(BaseCommand):
    help = 'Count first authorships by author over a specified period of time'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int,
                            help="Year to count for.")

    def handle(self, *args, **options):
        year = options["year"]
        print("CountAuthors for year {0}". \
              format(str(year)))
        author_list = process(year)
        for item in author_list:
            print(item[0], item[1])
