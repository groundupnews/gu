from django.db.models import Q, F
from newsroom.models import Article, Author, Category, Topic
from gallery.models import Photograph
from django.utils import timezone

from django.contrib.postgres.search import SearchVector, SearchRank, \
    SearchQuery

import shlex
import string


def parseSearchString(search_string):
    try:
        search_strings = shlex.split(search_string)
        translator = str.maketrans({key: None for key in string.punctuation})
        search_strings = [s.translate(translator) for s in search_strings]
    except:
        search_strings = []
    return search_strings


def createSearchQuery(list_of_terms):
    if len(list_of_terms) > 0:
        q = SearchQuery(list_of_terms[0])
        for term in list_of_terms[1:]:
            q = q & SearchQuery(term)
        return q
    else:
        return None


def searchPostgresDB(search_string, Table, config, rank, *fields):
    list_of_terms = parseSearchString(search_string)
    search_query = createSearchQuery(list_of_terms)
    if rank is True:
        vector = SearchVector(*fields, config=config)
        objs = Table.objects.annotate(rank=SearchRank(vector, search_query)).\
            order_by('-rank')
    else:
        objs = Table.objects.annotate(search=SearchVector(*fields,
                                                          config=config),).\
                filter(search=search_query)
    return objs


def searchArticles(search_string=None,
                   author_pk=None, first_author=False,
                   category_pk=None, topic_pk=None,
                   from_date=None, to_date=None):
    query = Q()
    if search_string:
        list_of_terms = parseSearchString(search_string[:30])
        for term in list_of_terms:
            if term not in ["and", "or", "of", "but", "on", "is", ]:
                query = query & \
                        (Q(title__icontains=term) |
                         Q(subtitle__icontains=term) |
                         Q(primary_image_caption__icontains=term) |
                         Q(cached_byline_no_links__icontains=term) |
                         Q(body__icontains=term))
    if author_pk:
        try:
            author = Author.objects.get(pk=author_pk)
            if first_author is True:
                query = query & Q(author_01=author)
            else:
                query = query & (Q(author_01=author) |
                                 Q(author_02=author) |
                                 Q(author_03=author) |
                                 Q(author_04=author) |
                                 Q(author_05=author))
        except:
            pass

    if category_pk:
        try:
            category = Category.objects.get(pk=category_pk)
            query = query & Q(category=category)
        except:
            pass

    if topic_pk:
        try:
            topic = Topic.objects.get(pk=topic_pk)
            query = query & Q(topics=topic)
        except:
            pass

    if from_date:
        try:
            dt = timezone.datetime.strptime(from_date,"%Y%m%d").date()
            query = query & Q(published__gte=dt)
        except:
            pass

    if to_date:
        try:
            dt = timezone.datetime.strptime(to_date,"%Y%m%d").date()
            query = query & Q(published__lte=dt)
        except:
            pass

    articles = Article.objects.published().filter(query).order_by("-published").distinct()

    return articles


def searchPhotos(search_string=None,
                 author_pk=None,
                 from_date=None, to_date=None):
    query = Q()

    if search_string:
        list_of_terms = parseSearchString(search_string[:30])
        for term in list_of_terms:
            if term not in ["and", "or", "of", "but", "on", "is", ]:
                query = query & \
                        (Q(suggested_caption__icontains=term) |
                         Q(alt__icontains=term) |
                         Q(keywords__name=term))

    if author_pk:
        try:
            author = Author.objects.get(pk=author_pk)
            query = query & Q(photographer=author)
        except:
            pass

    if from_date:
        try:
            dt = timezone.datetime.strptime(from_date,"%Y%m%d").date()
            query = query & Q(date_taken__gte=dt)
        except:
            pass

    if to_date:
        try:
            dt = timezone.datetime.strptime(to_date,"%Y%m%d").date()
            query = query & Q(date_taken__lte=dt)
        except:
            pass


    photos = Photograph.objects.filter(query).order_by("-date_taken").distinct()

    return photos

def searchArticlesAndPhotos(search_string=None,
                            inc_articles=True, inc_photos=None,
                            author_pk=None, first_author=False,
                            category_pk=None, topic_pk=None,
                            from_date=None, to_date=None):

    articles = photos = result = []
    if inc_articles:
        articles = searchArticles(search_string, author_pk, first_author,
                                  category_pk, topic_pk,
                                  from_date, to_date).extra(select = {'obj_type': 0}). \
                                  values("pk", "title", "subtitle", "cached_summary_image",
                                         "published", "obj_type", "slug")

    if inc_photos:
        photos = searchPhotos(search_string, author_pk,
                              from_date, to_date).extra(select = {'obj_type': 1}). \
                              values("pk", "suggested_caption", "alt", "image",
                                     "obj_type", "credit").annotate(published=F("date_taken"))

    if articles and photos:
        result = articles.union(photos).order_by('-published')
    elif articles:
        result = articles
    elif photos:
        result = photos
        
    return result
