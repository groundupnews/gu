from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView
from django.core.paginator import Paginator
#for api request
import requests
import json
import random
from datetime import datetime

from .models import Donor, Currency, Donation
from .forms import DonationForm, CurrencyForm, DonorForm

#Base page to be displayed
def page(request):
    #need to paginate the list
    latest_donations = Donation.objects.order_by('-datetime_of_donation')
    items_per_page = 20 
    paginator = Paginator(latest_donations, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    template = loader.get_template('donationPage/paginated.html')
    return HttpResponse(template.render(context,request))
    #context ={'latest_donations':latest_donations,'form':form,}
    #return HttpResponse(template.render(context,request))

#dashboard page to be displayed when a donor url is accessed
def donorDash(request, donor_url):
    Cdonor=Donor.objects.get(donor_url=donor_url)
    donations = Donation.objects.all().filter(donor=Cdonor)     
    form = DonorForm(instance=Cdonor)
    link=donor_url+"?update"
    context = {'donations':donations, 'link':link, 'form':form,}
    template = loader.get_template('donationPage/dashboard.html')
    return HttpResponse(template.render(context, request))


##Api call, to be tested.

def fetch_snapscan_transactions():
    url = "https://api.snapscan.io/v1/transactions"
    headers = {
        "Authorization": "Bearer YOUR_API_KEY_HERE",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        transactions = json.loads(response.text)
        return transactions["data"]
    else:
        return []


def make_donorUrl():
    min_val = 100000000000000000000000000000000000
    max_val = 999999999999999999999999999999999999

    # Get the current date and time as a numeric-only 14-digit string
    current_date = datetime.now()
    date_string = current_date.strftime("%Y%m%d%H%M%S")

    # Generate a random 36-digit number
    url = str(random.randint(min_val, max_val))

    # Concatenate the random number and date
    url += date_string

    return url

def save_transactions_to_database():
    transactions = fetch_snapscan_transactions()
    for donation in transactions:
        donor_email = donation["reference"]
        amount = donation["amount"]
        currency_type = donation["currency_type"]
        datetime_of_donation = donation["datetime_of_donation"]
        notified = False
        section18a = False

        Cdonor=Donor.objects.get(donor_url=donor_url)
        if not Cdonor:
            url=make_donorUrl()
            newDonor = Donor(email=donor_email, name="anonymous", display_name="anonymous", donor_url=url)
        # Create a new Donation object and save it to the database
        new_donation = Donation(donor=reference, amount=amount, datetime_of_donation=datetime_of_donation, currency_type=currency_type, notified=notified, section18a=section18a)
        new_donation.save()


