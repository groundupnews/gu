import urllib
import hashlib
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
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
    url=donor_url
    Cdonor=Donor.objects.get(donor_url=url)
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
            messages.add_message(request, messages.INFO,"Details updated.")
            return redirect('donation.dashboard', donor_url=donor_url)  
    return HttpResponse(template.render(context, request))


def payment_success(request):
    return render(request, 'payfast/success.html')


def payment_cancel(request):
    return render(request, 'payfast/cancel.html')


def payment_notify(request):
    # Here, you need to handle the server-to-server communication and validate the payment.
    return HttpResponse("Payment notification received", status=200)


def payment_view(request):
    default_amount = 100  # ZAR
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            'merchant_id': settings.PAYFAST_MERCHANT_ID,
            'merchant_key': settings.PAYFAST_MERCHANT_KEY,
            'return_url': settings.PAYFAST_RETURN_URL,
            'cancel_url': settings.PAYFAST_CANCEL_URL,
            'notify_url': settings.PAYFAST_NOTIFY_URL,
            'name_first': request.POST.get("first_name"),
            'name_last': request.POST.get("last_name"),
            'email_address': request.POST.get("email"),
            'amount': request.POST.get("amount", default_amount)
        }

        subscription_type = request.POST.get("subscription_type", "monthly")

        if subscription_type == "monthly":
            data['item_name'] = 'Monthly Subscription'
            data['subscription_type'] = 1
            data['billing_date'] = str(timezone.now().date())
            data['recurring_amount'] = request.POST.get("amount", default_amount)
            data['frequency'] = 3
            data['cycles'] = 0
        else:
            data['item_name'] = 'One Time Payment'

        # Create signature (MD5 hash of parameters)
        signature = generate_signature(data, settings.PAYFAST_PASS_PHRASE)
        data['signature'] = signature

        rendered_html = render(
            request, 'payfast/payment_form.html', {"data": data}
        ).content.decode('utf-8')
        return JsonResponse({'html': rendered_html}, status=200)

    return render(request, 'payfast/payment.html', {'default_amount': default_amount})


def generate_signature(data, pass_phrase=None):
    # Create parameter string
    pf_output = ''
    for key, val in data.items():
        if val != '':
            pf_output += f'{key}={urllib.parse.quote_plus(str(val).strip())}&'
    # Remove last ampersand
    get_string = pf_output[:-1]
    # Add passphrase if provided
    if pass_phrase is not None:
        get_string += f'&passphrase={urllib.parse.quote_plus(pass_phrase.strip())}'
    # Return the MD5 hash of the string
    return hashlib.md5(get_string.encode()).hexdigest()