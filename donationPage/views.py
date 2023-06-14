from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView
from django.core.paginator import Paginator
#for api request
import requests
import json

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


def save_transactions_to_database():
    transactions = fetch_snapscan_transactions()
    for donation in transactions:
        reference = donation["reference"]
        amount = donation["amount"]
        currency_type = donation["currency_type"]
        datetime_of_donation = donation["datetime_of_donation"]
        notified = False
        section18a = False
        # Create a new Transaction object and save it to the database
        new_donation = Donation(donor=reference, amount=amount, datetime_of_donation=datetime_of_donation, currency_type=currency_type, notified=notified, section18a=section18a)
        new_donation.save()


