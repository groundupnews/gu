from django.core.management.base import BaseCommand, CommandError
from newsroom.models import Article

from django.contrib.sites.models import Site

def process(site_name, site_domain):
    site = Site.objects.get_current()
    site.name = site_name
    site.domain = site_domain
    site.save()

class Command(BaseCommand):
    help = 'Set name and domain of site'

    def add_arguments(self, parser):
        parser.add_argument('site_name')
        parser.add_argument('site_domain')

    def handle(self, *args, **options):
        process(options["site_name"], options["site_domain"])
