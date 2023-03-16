from ajax_select import LookupChannel, register
from django.db.models import Q
from newsroom.models import Article, Author, Topic


@register('articles')
class ArticleLookup(LookupChannel):

    model = Article

    def get_query(self, q, request):
        query = Q(title__icontains=q) | Q(pk__icontains=q) | \
                Q(subtitle__icontains=q)
        return self.model.objects.published().filter(query).\
            order_by("-pk")[:10]

    def format_item_display(self, item):
        return str(item)

@register('authors')
class AuthorLookup(LookupChannel):

    model = Author

    help_text = "Name of author"

    def get_query(self, q, request):
        #split the input on whitespace, this doubles to strip the input of problematic whitespace
        #doesn't support multi word names since whitespace is removed the database won't match (RSM SA Consulting (Pty) Ltd won't autocomplete beyond a single word match)
        arr=q.split()
        #check if the input has more than one word as search terms
        if len(arr)>1:
            query = Q(first_names__icontains=arr[0]) & Q(last_name__icontains=arr[1]) | Q(pk__icontains=q)
        else:
            #we must use array[0] since q may contain the whitespace that breaks the search. 
            query = Q(first_names__icontains=arr[0]) | Q(last_name__icontains=arr[0]) | Q(pk__icontains=arr[0])        
                    
        return self.model.objects.filter(query).filter(email__isnull=False).\
            order_by("last_name")

    def format_item_display(self, item):
        return str(item)


@register('authors_only')
class AuthorOnlyLookup(LookupChannel):
    '''
    Only includes real authors as opposed to companies used to
    pay requisitions to etc.
    '''
    model = Author

    help_text = "Name of author"

    def check_auth(self, request):
        return True

    def get_query(self, q, request):
        if ' ' in q:
            arr=q.split()
            query = Q(first_names__icontains=arr[0]) & Q(last_name__icontains=arr[1]) | Q(pk__icontains=q)
                    
        else:
            query = Q(last_name__icontains=q) | Q(pk__icontains=q) | \
                    Q(first_names__icontains=q)
        return self.model.objects.filter(query).\
            exclude(freelancer='t').\
            filter(email__isnull=False).\
            order_by("last_name")

    def format_item_display(self, item):
        return str(item)


@register('topics')
class TopicLookup(LookupChannel):

    model = Topic

    help_text = "Topic"

    def get_query(self, q, request):
        query = Q(name__icontains=q) | Q(pk__icontains=q) | \
                Q(slug__icontains=q)
        return self.model.objects.filter(query).order_by("name")

    def format_item_display(self, item):
        return str(item)
