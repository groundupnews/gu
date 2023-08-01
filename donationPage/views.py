from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Donor, Currency, Donation
from .forms import DonationForm, CurrencyForm, DonorForm

#Base page to be displayed
def page(request):
    latest_donations = Donation.objects.order_by('-datetime_of_donation')
    for donation in latest_donations:
        donation.datetime_of_donation = donation.datetime_of_donation.strftime("%Y-%m-%d")
        donation.amount = "{:,.2f}".format(donation.amount)
    items_per_page = 20 
    paginator = Paginator(latest_donations, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    template = loader.get_template('donationPage/paginated.html')
    return HttpResponse(template.render(context,request))
    

#dashboard page to be displayed when a donor url is accessed
def donorDash(request, donor_url):
    Cdonor=Donor.objects.get(donor_url=donor_url)
    donations = Donation.objects.all().filter(donor=Cdonor)     
    form = DonorForm(instance=Cdonor)
    for donation in donations:
        donation.datetime_of_donation=donation.datetime_of_donation.strftime("%Y-%m-%d")
        donation.amount = "{:,.2f}".format(donation.amount)
    context = {'donations':donations, 'form':form,}
    template = loader.get_template('donationPage/dashboard.html')
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            # Get the user profile based on the email (or any other unique identifier)
            user_profile, created = Donor.objects.get_or_create(email=form.cleaned_data['email'])
            
            # Update the fields with the submitted data
            user_profile.name = form.cleaned_data['name']
            user_profile.display_name = form.cleaned_data['display_name']
            user_profile.email = form.cleaned_data['email']
            
            # Save the updated user profile to the database
            user_profile.save()
            messages.add_message(request, messages.INFO,
                                 "Details updated.")
            return redirect('donation.dashboard', donor_url=donor_url)  # Redirect to the dashboard page or any other page
   
    return HttpResponse(template.render(context, request))



