import datetime
from django.core.management.base import BaseCommand
from newsroom.wetell import fetch_save_wetell

class Command(BaseCommand):
    help = 'Fetches latest Wetell bulletin from a given service'

    def add_arguments(self, parser):
        parser.add_argument('service', type=int,
                            help="Service id")


    def handle(self, *args, **options):
        service = options['service']
        print("Fetch wetell: {}:".format(str(service)))
        fetch_save_wetell(service)
