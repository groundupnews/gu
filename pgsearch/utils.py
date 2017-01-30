from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery

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
    if rank == True:
        vector = SearchVector(*fields, config=config)
        objs = Table.objects.annotate(rank=SearchRank(vector, search_query)).\
               order_by('-rank')
    else:
        objs = Table.objects.annotate(search=SearchVector(*fields,
                                                          config=config),).\
                filter(search=search_query)
    return objs
