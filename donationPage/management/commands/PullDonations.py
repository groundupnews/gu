import requests
import json
import random
import pytz
import re
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime, timezone, timedelta
from requests.auth import HTTPBasicAuth
from donationPage.models import Donor, Currency, Donation
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

def handle_transaction(donor_email, donor_name, transaction_datetime, amount, currency_type, notified, count):
        count=count
        try:
            Cdonor=Donor.objects.get(email=donor_email)
        except:
        #create new donor entry if not, and set Cdonor value to newDonor data
            url=make_donorUrl(transaction_datetime).replace("UTC","")
            newDonor = Donor(email=donor_email, name=donor_name, display_name='Anonymous', donor_url=url)
            newDonor.save()
            Cdonor=newDonor
            
        #duplicate donation protection
        try:
            Cdonation=Donation.objects.get(donor=Cdonor, amount=amount, datetime_of_donation=transaction_datetime)
        except:
        # Create a new Donation object and save it to the database
            count=count+1
            if is_valid_email(donor_email):
                # Send the email with the unique link
                subject = 'Thank you for your donation to GroundUp'
                email_url = "https://www.groundup.org.za/donation/"+Cdonor.donor_url
                message = render_to_string('donationPage/email_template.html', {'unique_link': email_url, 'donor_name': donor_name})
                plain_message = strip_tags(message)
                
                send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [donor_email], html_message=message)
                notified=True

            new_donation = Donation(donor=Cdonor, amount=amount, datetime_of_donation=transaction_datetime, currency_type=currency_type, notified=notified, section18a_issued=False)
            new_donation.save()
        return count

def fetch_snapscan_transactions():
    response = requests.get(settings.SS_URL, auth=HTTPBasicAuth(settings.SS_API_KEY,''))
    #the transactions object is an array of dictionaries containing all the transactions for our snapscan account. 
    #to access the elements of a transaction the reference is transactions[i]["Key Value"]
    if response.status_code == 200:
        transactions = json.loads(response.text)
        return transactions
    else:
        print("Snapscan fetch fail: ", response.status_code)
        return []

def fetch_givengain_transactions():
    #GivenGain uses utf-8 encoding for the auth, so HTTPBasicAuth produces 401 errors
    key="APIkey "+settings.GG_API_KEY
    response = requests.get(settings.GG_URL, headers={"Authorization":key})
    #the transactions object is an array of dictionaries containing all the transactions for our snapscan account. 
    #to access the elements of a transaction the reference is transactions[i]["Key Value"]
    if response.status_code == 200:
        transactions = json.loads(response.text)
        return transactions
    else:
        print("GivenGain fetch fail: ", response.status_code)
        return []

def fetch_paypal_transactions():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    #datetime result 2023-07-24 19:29:53.624990
    end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S-0700')
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S-0700')
    #PayPal requires a start and end date so we edit the url per request, We also can't query a timeframe longer than 31 days
    pp_url = settings.PP_URL.replace("**", start_date_str).replace("^^", end_date_str)

    data = {
        'grant_type': 'client_credentials',
    }
    #generate access token
    authToken = requests.post('https://api-m.paypal.com/v1/oauth2/token', data=data, auth=(settings.PP_ID, settings.PP_SECRET))

    if authToken.status_code == 200:
        access_token = authToken.json().get("access_token")
        #check that access token was received
        if not access_token:
            print("PayPal access token not found in response.")
            
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        #query for recent transactions
        response = requests.get(pp_url, headers=headers)
        if response.status_code == 200:
            transactions = json.loads(response.text)
            return transactions
        else:
            print("PayPal fetch fail: ", response.status_code, response.text)
            return []
            
    else:
        print("Failed to get PayPal access token: ", authToken.status_code, authToken.text)
        return []

def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email)

def make_donorUrl(date):
    min_val = 100000000000000000000000000000000000
    max_val = 999999999999999999999999999999999999

    # Format for desired output
    output_format = "%Y%m%d%H%M%Z"
    if date:
        # Convert the datetime object to a string
        date_string = date.strftime(output_format)
    else:
        date_string = datetime.now().strftime(output_format)
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
        amount = donation["totalAmount"]/100
        #for snapscan these will be static but they may be useful for the other apis
        currency_type = Currency.objects.get(currency_abr="ZAR")

        # Input date string
        date_string = donation["date"]

        # Define the format matching the input date string
        date_format = "%Y-%m-%dT%H:%M:%SZ"

        # Convert the date string to a datetime object
        datetime_of_donation = datetime.strptime(date_string, date_format)
        datetime_of_donation = datetime_of_donation.replace(tzinfo=pytz.utc)
       
        notified = False
        section18a = False
        
        
        count=handle_transaction(donor_email, donor_name, datetime_of_donation, amount, currency_type, notified, count)
            
    return count

def pullPayPal():
    transactions = fetch_paypal_transactions()
    count=0
    for donation in transactions.get("transaction_details", []):
        transaction_info = donation.get("transaction_info", {})
        payer_info = donation.get("payer_info", {})

        # Get payer email with error handling
        try:
            donor_email = payer_info["email_address"]
        except KeyError:
            donor_email = "PayPal anonymous"+transaction_info.get("transaction_initiation_date", "")

        # Get payer name with error handling
        try:
            given_name = payer_info["payer_name"]["given_name"]
        except KeyError:
            given_name = ""
        try:
            surname = payer_info["payer_name"]["surname"]
        except KeyError:
            surname = ""
        
        # Combine payer name components (given_name and surname) and handle missing name
        if given_name and surname:
            donor_name = given_name + " " + surname
        elif given_name:
            donor_name = given_name
        elif surname:
            donor_name = surname
        else:
            donor_name = "Anonymous"  # Set a default name if both components are missing

        transaction_datetime_str = transaction_info.get("transaction_initiation_date", "")
        amount = transaction_info.get("transaction_amount", {}).get("value", "")
        currency_type = Currency.objects.get(currency_abr=transaction_info.get("transaction_amount", {}).get("currency_code", ""))

        # Convert the datetime string to a timezone-aware datetime object
        try:
            transaction_datetime = datetime.strptime(transaction_datetime_str, "%Y-%m-%dT%H:%M:%S%z")
            transaction_datetime = transaction_datetime.astimezone(pytz.UTC)
        except ValueError:
            transaction_datetime = None  # Set default value if the datetime string is invalid

        #for paypal these will be static but they may be useful for the other apis
        notified = False
        section18a = False
        
        count=handle_transaction(donor_email, donor_name, transaction_datetime, amount, currency_type, notified, count)
    return count

def pullGivenGain():
    transactions = fetch_givengain_transactions()
    count=0
    for donation in transactions["donations"]:
        #t
        try:
            donor_email = donation["donor"]["url"]
        except:
            donor_email = "GivenGain ID:"+donation["donor"]["id"]
        try:
            donor_name = donation["donor"]["first_name"]+" "+donation["donor"]["last_name"]
        except:
            donor_name = "Anonymous"
        #Amount excludes fees but this is what the donor paid. it is also currency sensitive
        amount = donation["amount"]
        currency_type = Currency.objects.get(currency_abr=donation["currency"]["code"])
        #add datetime constructor once date format is known
        input_date_str = donation["transaction_date"]
        datetime_of_donation = datetime.strptime(input_date_str, "%Y-%m-%d").replace(hour=0, minute=0)
        datetime_of_donation = datetime_of_donation.replace(tzinfo=pytz.utc)
        #for givengain these will be static but they may be useful for the other apis
        notified = False
        section18a = False
        
        count=handle_transaction(donor_email, donor_name, datetime_of_donation, amount, currency_type, notified, count)
    return count


def process():
    new_ss=pullSnapScan()
    new_gg=pullGivenGain()
    new_pp=pullPayPal()
    return (new_ss,new_pp,new_gg)

class Command(BaseCommand):
    help = 'Perform API calls to update donations database.'

    def handle(self, *args, **options):
        results = process()
        print("SnapScan: {0}. "
              "PayPal: {1}. "\
              "GivenGain: {2}".\
              format(results[0], results[1], results[2],))
