from django.core.management.base import BaseCommand, CommandError
from newsroom.models import Article, Author
from django.utils import timezone
from django.db.models import Count

def process(year, author_no=1):
    date_from = timezone.datetime(year=year, month=1, day=1)
    date_to = timezone.datetime(year=year, month=12, day=31)
    articles = Article.objects.published().filter(published__gte=date_from). \
               filter(published__lte=date_to)
    authors = Author.objects.all()
    author_field = "author_01"
    if author_no == 2:
        author_field = "author_02"
    elif author_no == 3:
        author_field = "author_03"
    elif author_no == 4:
        author_field = "author_04"
    elif author_no == 5:
        author_field = "author_04"                
        
    count = articles.values(author_field).annotate(total=Count('author_01')).\
        order_by('-total')
    result = []
    for item in count:
        pk = pk=item[author_field]
        if pk:
            author = str(Author.objects.get(pk=item[author_field]))
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

        parser.add_argument('author_no', nargs='?', type=int,
                            help="Author number", default=1)
        

    def handle(self, *args, **options):
        year = options["year"]
        author_no = options["author_no"]
        print("CountAuthors for year {0}. Author # {1}.". \
              format(str(year),str(author_no)))
        author_list = process(year, author_no)
        for item in author_list:
            print(item[0], item[1])
