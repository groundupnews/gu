import datetime
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from newsroom.models import Article
from newsroom.models import MostPopular

def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
    """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

    f = open(key_file_location, 'rb')
    key = f.read()
    f.close()

    credentials = SignedJwtAssertionCredentials(service_account_email, key,
                                              scope=scope)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    service = build(api_name, api_version, http=http)

    return service


def get_first_profile_id(service):
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for this user
    accounts = service.management().accounts().list().execute()

    if accounts.get('items'):
        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(
        accountId=account).execute()

        if properties.get('items'):
            # Get the first property id.
            property = properties.get('items')[0].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                accountId=account,
                webPropertyId=property).execute()

            if profiles.get('items'):
                # return the first view (profile) id.
                return profiles.get('items')[0].get('id')

    return None


def get_results(service, profile_id, days):
    # Use the Analytics Service Object to query the Core Reporting API
    # for the number of sessions within the past seven days.
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date = str(days)+ 'daysAgo',
        end_date = 'today',
        sort = '-ga:pageviews',
        dimensions = 'ga:pageTitle,ga:pagePath',
        metrics = 'ga:pageviews,ga:uniquePageviews').execute()


def process(days, num_articles):
    # Define the auth scopes to request.
    scope = ['https://www.googleapis.com/auth/analytics.readonly']

    # Use the developer console and replace the values with your
    # service account email and relative location of your key file.
    # service_account_email = 'groundup@guanalytics-1207.iam.gserviceaccount.com'
    service_account_email = settings.GOOGLE_ANALYTICS_EMAIL
    key_file_location = settings.GOOGLE_ANALYTICS_PRIVATEKEY_FILE

    # Authenticate and construct service.
    service = get_service('analytics', 'v3', scope, key_file_location,
                          service_account_email)
    profile = get_first_profile_id(service)
    results = get_results(service, profile, days)

    num_found = 1
    article_list = []
    for result in results.get("rows"):
        if num_found > num_articles:
            break
        if result[1][0:9] == "/article/":
            slug = result[1][9:-1]
            try:
                article = Article.objects.get(slug=slug)
                if not article.is_published():
                    continue
                if article.published >= timezone.now() - \
                   datetime.timedelta(days=days):
                    article_list.append(article.slug + "|" + article.title)
                    num_found = num_found + 1
            except ObjectDoesNotExist:
                continue
    mostpopular = MostPopular()
    mostpopular.article_list = "\n".join(article_list)
    mostpopular.save()

class Command(BaseCommand):
    help = 'Get the most popular GroundUp articles from Google Analytics'

    def add_arguments(self, parser):
        parser.add_argument('days', type=int,
                            help="Number of days back to consider.")
        parser.add_argument('numarticles', type=int,
                            help="Number of articles to include")

    def handle(self, *args, **options):
        days = options["days"]
        num_articles = options["numarticles"]
        print("Mostpopular: {0}: Processing {1} days back for {2} articles.". \
              format(str(timezone.now()), days, num_articles))
        process(days, num_articles)
