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
        query = Q(last_name__icontains=q) | Q(pk__icontains=q) | \
                Q(first_names__icontains=q)
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

    def get_query(self, q, request):
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
