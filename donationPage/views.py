import json
import urllib
import hashlib
import requests
import logging
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Donor, Donation, Subscription, Currency
from .forms import DonorForm, PayfastPaymentForm
from donationPage.utils import make_donorUrl

signer = TimestampSigner()
logger = logging.getLogger("django")


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
            messages.add_message(request, messages.INFO, "Details updated.")
            return redirect('donation.dashboard', donor_url=donor_url)
    return HttpResponse(template.render(context, request))


def donor_access_view(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get("email", None)
        if email:
            context["email"] = email
            donor = Donor.objects.filter(email=email).first()
            if not donor:
                context["error"] = "donor_not_found"
            else:
                token = signer.sign(donor.donor_url)
                access_link = reverse('donor_dashboard', kwargs={'token': token})
                full_access_link = request.build_absolute_uri(access_link)
                subject = 'Access Your Donor Dashboard'
                message = loader.render_to_string('payfast/email/dashboard_access.html', {
                    'donor': donor,
                    'access_link': full_access_link,
                })
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [donor.email],
                        html_message=message,
                    )
                    context["email_sent"] = True
                except Exception as e:
                    context["error"] = "error_sending_email"
    return render(
        request,
        'payfast/donor_access.html',
        context
    )


def donor_dashboard_view(request, token):
    try:
        donor_url = signer.unsign(token, max_age=86400)  # 24 hours in seconds
        donor = get_object_or_404(Donor, donor_url=donor_url)
        donor_form = DonorForm(instance=donor)
        donations = Donation.objects.filter(donor=donor).order_by("-datetime_of_donation")
        paginator = Paginator(donations, 5)
        page_number = request.GET.get('page')
        donations_page_obj = paginator.get_page(page_number)
        subscriptions = Subscription.objects.filter(donor=donor).order_by("-created_at")

        if request.method == "POST":
            donor_form = DonorForm(request.POST)
            if donor_form.is_valid():
                donor.email = donor_form.cleaned_data.get("email", donor.email)
                donor.name = donor_form.cleaned_data.get("name", donor.name)
                donor.display_name = donor_form.cleaned_data.get("display_name", donor.display_name)
                donor.save()
                messages.add_message(
                    request,
                    messages.INFO,
                    "Updated donor details"
                )
        return render(request, 'payfast/donor_dashboard.html', {
            'donor': donor,
            'donations': donations_page_obj,
            'subscriptions': subscriptions,
            'donor_form': donor_form,
            'token': token
        })
    except (BadSignature, SignatureExpired):
        # Handle invalid or expired token
        return HttpResponse("Invalid or expired link.", status=400)


def cancel_subscription(request, token):
    try:
        if request.method == "POST":
            donor_url = signer.unsign(token, max_age=86400)
            donor = get_object_or_404(Donor, donor_url=donor_url)
            subscription_id = request.POST.get("subscription_id")
            subscription = Subscription.objects.filter(
                id=subscription_id,
                status='active',
                donor=donor
            ).first()

            if subscription:
                cancel_url = f"https://api.payfast.co.za/subscriptions/{subscription.subscription_id}/cancel"
                if settings.PAYFAST_TEST_MODE:
                    cancel_url += "?testing=true"
                now = timezone.now()
                formatted_now = now.strftime('%Y-%m-%dT%H:%M:%S%z')
                if not formatted_now.endswith('+00:00'):
                    formatted_now = formatted_now[:-5]

                pf_data = [
                    ("merchant-id", settings.PAYFAST_MERCHANT_ID),
                    ("passphrase", settings.PAYFAST_PASS_PHRASE.strip()),
                    ("timestamp", formatted_now),
                    ("version", "v1")
                ]
                pfParamString = ''
                for row in pf_data:
                    pfParamString += row[0] + "=" + urllib.parse.quote_plus(row[1]) + "&"
                pfParamString = pfParamString[:-1]
                signature = hashlib.md5(pfParamString.encode()).hexdigest()

                headers = {
                    'merchant-id': settings.PAYFAST_MERCHANT_ID,
                    'version': 'v1',
                    'timestamp': formatted_now,
                    'signature': signature
                }
                response = requests.put(cancel_url, headers=headers)
                if response.status_code == 200:
                    subscription.status = "canceled"
                    subscription.save()
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Your subscription was canceled successfully"
                    )
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "There was an error canceling your subscription. Please try again later!"
                    )

        return redirect('donor_dashboard', token=token)
    except (BadSignature, SignatureExpired):
        # Handle invalid or expired token
        return HttpResponse("Invalid or expired link.", status=400)


def payment_success(request):
    return render(request, 'payfast/success.html')


def payment_cancel(request):
    messages.add_message(
        request,
        messages.ERROR,
        "Your donation transaction was cancelled. If this was a mistake, you can try again by using form below."
    )
    return redirect('make_payment')


def payment_view(request):
    default_amount = 100

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = PayfastPaymentForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            name = form.cleaned_data.get("name")
            display_name = form.cleaned_data.get("display_name")
            amount = form.cleaned_data.get("amount", default_amount)
            payment_type = form.cleaned_data.get("payment_type")

            data = {
                'merchant_id': settings.PAYFAST_MERCHANT_ID,
                'merchant_key': settings.PAYFAST_MERCHANT_KEY,
                'return_url': settings.PAYFAST_RETURN_URL,
                'cancel_url': settings.PAYFAST_CANCEL_URL,
                'notify_url': settings.PAYFAST_NOTIFY_URL,
            }

            if first_name:
                data['name_first'] = first_name
            else:
                data['name_first'] = name

            if last_name:
                data["name_last"] = last_name

            data["email_address"] = email
            data["amount"] = amount

            donor = Donor.objects.filter(email=email).first()
            if donor:
                if not donor.name:
                    donor.name = name
                    donor.display_name = display_name
                    donor.save()
            else:
                donor = Donor.objects.create(
                    email=email, name=name,
                    display_name=display_name,
                    donor_url=make_donorUrl()
                )

            if payment_type == "subscription":
                data['item_name'] = 'Monthly Donation'
                data['subscription_type'] = 1
                data['billing_date'] = str(timezone.now().date())
                data['recurring_amount'] = amount
                data['frequency'] = 3
                data['cycles'] = 0
            else:
                data['item_name'] = 'One Time Donation'

            # Create signature (MD5 hash of parameters)
            signature = generate_signature(data, settings.PAYFAST_PASS_PHRASE)
            data['signature'] = signature
            data['payfast_domain'] = settings.PAYFAST_URL

            rendered_html = render(
                request, 'payfast/payment_form.html', {"data": data}
            ).content.decode('utf-8')
            return JsonResponse({'html': rendered_html}, status=200)
        else:
            return JsonResponse({"errors": form.errors}, status=200)

    form = PayfastPaymentForm()
    return render(request, 'payfast/payment.html', {'form': form})


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


@csrf_exempt
def payfast_ipn(request):
    if request.method == 'POST':
        data = request.POST.dict()
        # Extract the signature from the received data
        received_signature = data.get('signature', '')
        # Verify the signature
        if verify_payfast_signature(data, received_signature):
            # Process IPN data
            payment_status = data.get('payment_status')
            subscription_id = data.get('token', None)
            transaction_id = data.get('pf_payment_id')
            amount_gross = data.get('amount_gross')
            email_address = data.get('email_address')
            donor = Donor.objects.filter(email=email_address).first()
            currency, _ = Currency.objects.get_or_create(
                currency_abr="ZAR"
            )
            subscription_id = data.get('token', None)
            payment_type = "subscription" if subscription_id else "one_time"
            payment_success = "success" if payment_status == "COMPLETE" else "failed"

            if payment_type == 'subscription':
                subscription = Subscription.objects.filter(
                    subscription_id=subscription_id
                ).first()

                if not subscription:
                    subscription = Subscription.objects.create(
                        donor=donor,
                        subscription_id=subscription_id,
                        status='pending',
                        amount=amount_gross,
                    )

                if payment_status == 'COMPLETE':
                    subscription.status = 'active'
                    subscription.failed_payments = 0
                    subscription.save()

                elif payment_status == 'FAILED':
                    # Handle failed payment
                    subscription.failed_payments += 1
                    if subscription.failed_payments >= 3:
                        subscription.status = 'suspended'
                    subscription.save()

            Donation.objects.create(
                donor=donor,
                transaction_id=transaction_id,
                amount=amount_gross,
                payment_type=payment_type,
                datetime_of_donation=timezone.now(),
                currency_type=currency,
                status=payment_success,
                platform='payfast'
            )
            return HttpResponse(status=200)
    return HttpResponse(status=400)


def verify_payfast_signature(postData, received_signature):
    pfParamString = ''
    for key, value in postData.items():
        if key != "signature":
            pfParamString += key + "=" + urllib.parse.quote_plus(value) + "&"
    # Generate our signature from Payfast parameters
    pfParamString = pfParamString[:-1]
    pfParamString += f'&passphrase={urllib.parse.quote_plus(settings.PAYFAST_PASS_PHRASE.strip())}'
    signature = hashlib.md5(pfParamString.encode()).hexdigest()
    return (received_signature == signature)
