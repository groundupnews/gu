import requests
import json
from newsroom.models import WetellBulletin

def fetch_wetell(service_id):
    url = "https://wetell.news/api/bulletin/by_service/latest/" \
        + str(service_id) + "/"
    r = requests.get(url=url)
    data = r.json()
    return data

def save_wetell(data):
    if WetellBulletin.objects.filter(
            service=data['key']).filter(published=data['published']).exists():
        bulletin = WetellBulletin.objects.get(service=data['key'],
                             published=data['published'])
    else:
        bulletin = WetellBulletin()
        bulletin.service = data['key']
        bulletin.published = data['published']
    # Rather store json in the database than a Python object.
    # This does reverse what was done in fetch_wetell, but rather safe
    # than sorry.
    bulletin.data = json.dumps(data)
    bulletin.save()

def fetch_save_wetell(service_id):
    data = fetch_wetell(service_id)
    save_wetell(data)
