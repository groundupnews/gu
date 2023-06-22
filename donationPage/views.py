from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView
from django.core.paginator import Paginator

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
    #this link must be reworked to submit the update form and change the donor details
    link=donor_url+"?update"
    context = {'donations':donations, 'link':link, 'form':form,}
    template = loader.get_template('donationPage/dashboard.html')
    return HttpResponse(template.render(context, request))




