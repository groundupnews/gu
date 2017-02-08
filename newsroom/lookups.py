from ajax_select import register, LookupChannel
from newsroom.models import Article, Author
from django.db.models import Q

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

    help_text = "Hello!"

    def get_query(self, q, request):
        query = Q(last_name__icontains=q) | Q(pk__icontains=q) | \
                Q(first_names__icontains=q)
        return self.model.objects.filter(query).filter(email__isnull=False).\
            order_by("last_name")

    def format_item_display(self, item):
        return str(item)
