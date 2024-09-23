from django.core.management.base import BaseCommand
from django.core.cache import caches


class Command(BaseCommand):
    help = 'Clear the cache'

    def handle(self, *args, **options):
        cache = caches['default']
        cache.clear()
