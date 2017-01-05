import datetime
from haystack import indexes
from newsroom.models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='cached_byline')
    published = indexes.DateTimeField(model_attr='published')

    def get_updated_field(self):
        return 'modified'

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return self.get_model().objects.published().order_by("-published")
