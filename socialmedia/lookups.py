from ajax_select import LookupChannel, register
from django.db.models import Q
from socialmedia.models import TwitterHandle

@register('twitterhandles')
class TwitterHandleLookup(LookupChannel):

    model = TwitterHandle
    help_text = "Twitter user"


    def get_query(self, q, request):
        query = Q(name__icontains=q) | Q(slug__icontains=q)
        return self.model.objects.filter(query).order_by("name")

    def format_item_display(self, item):
        return str(item)
