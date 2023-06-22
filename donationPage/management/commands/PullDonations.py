import requests
import json
import random
from datetime import datetime
from requests.auth import HTTPBasicAuth
from donationPage.models import Donor, Currency, Donation
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

##Api call, to be tested.

def fetch_snapscan_transactions():
    #replace this hardcode with a settings reference.
    #url = "https://pos.snapscan.io/merchant/api/v1/payments"
    #response = requests.get(url, auth=HTTPBasicAuth('076db3e2-3015-4a0d-96c7-fe9c2bf3eb80',''))
    response = requests.get(settings.SS_URL, auth=HTTPBasicAuth(settings.SS_API_KEY,''))
    #the transactions object is an array of dictionaries containing all the transactions for our snapscan account. 
    #to access the elements of a transaction the reference is transactions[i]["Key Value"]
    if response.status_code == 200:
        transactions = json.loads(response.text)
        return transactions
    else:
        print("Snapscan fetch fail: "+response.status_code)
        return []


def make_donorUrl(date):
    min_val = 100000000000000000000000000000000000
    max_val = 999999999999999999999999999999999999

    # convert the date to a numeric-only 14-digit string
    date_string = date.replace("-","").replace(":","").replace("T","")[:-1]

    # Generate a random 36-digit number
    url = str(random.randint(min_val, max_val))

    # Concatenate the random number and date
    url += date_string

    return url

def pullSnapScan():
    transactions = fetch_snapscan_transactions()
    count=0
    for donation in transactions:
        #userReference is name, surname, email. We split these out into name and email some extra math is just to remove unnecessary characters from the start and end of each value
        donor_detail = donation["userReference"].split(",")
        donor_email = donor_detail[-1][1:]
        donor_name = donation["userReference"][:-len(donor_email)-2]
        #totalAmount excludes fees but this is what the donor paid.
        amount = donation["totalAmount"]
        
        #for snapscan these will be static but they may be useful for the other apis
        currency_type = Currency.objects.get(currency_abr="ZAR")
        datetime_of_donation = donation["date"]
        notified = False
        section18a = False
        
        
        #Fetch donor if exists
        try:
            Cdonor=Donor.objects.get(email=donor_email)
        except:
        #create new donor entry if not, and set Cdonor value to newDonor data
            url=make_donorUrl(datetime_of_donation)
            newDonor = Donor(email=donor_email, name=donor_name, display_name=donor_name, donor_url=url)
            newDonor.save()
            
            Cdonor=newDonor
        try:
            Cdonation=Donation.objects.get(donor=Cdonor, amount=amount, datetime_of_donation=datetime_of_donation)
        except:
        # Create a new Donation object and save it to the database
            new_donation = Donation(donor=Cdonor, amount=amount, datetime_of_donation=datetime_of_donation, currency_type=currency_type, notified=notified, section18a_issued=section18a)
            new_donation.save()
            count=count+1
    return count

def pullPayPal():
    return 0

def pullGivenGain():
    return 0

def process():
    new_ss=pullSnapScan()
    new_pp=pullPayPal()
    new_gg=pullGivenGain()
    return (new_ss,new_pp,new_gg)

class Command(BaseCommand):
    help = 'Perform API calls to update donations database.'

    def handle(self, *args, **options):
        results = process()
        print("SnapScan: {0}. "
              "PayPal: {1}. "\
              "GivenGain: {2}".\
              format(results[0], results[1], results[2],))
