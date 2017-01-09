from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery

import shlex
import string

def parseSearchString(search_string):
    print("D0:", search_string)
    search_strings = shlex.split(search_string)
    translator = str.maketrans({key: None for key in string.punctuation})
    search_strings = [s.translate(translator) for s in search_strings]
    print("D1:", search_strings)
    return search_strings

def createSearchQuery(list_of_terms):
    if len(list_of_terms) > 0:
        q = SearchQuery(list_of_terms[0])
        for term in list_of_terms[1:]:
            q = q & SearchQuery(term)
        return q
    else:
        return None

def searchPostgresDB(search_string, Table, rank, *fields):
    list_of_terms = parseSearchString(search_string)
    search_query = createSearchQuery(list_of_terms)
    if rank == True:
        vector = SearchVector(*fields)
        objs = Table.objects.annotate(rank=SearchRank(vector, search_query)).\
               order_by('-rank')
    else:
        objs = Table.objects.annotate(search=SearchVector(*fields),).\
               filter(search=search_query)
    return objs
