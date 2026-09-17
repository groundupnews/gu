import json
import urllib
import hashlib
import requests
import logging
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.template import loader
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Donor, Donation, Subscription, Currency, S18ACertificate
from .forms import (DonorForm, PayfastPaymentForm, CertificateRequestForm,
                    StaffCertificateForm, CertificateEmailForm)
from .pdf import certificate_filename, certificate_pdf_bytes
from . import sars
from . import settings as donation_settings
from donationPage.utils import make_donorUrl

signer = TimestampSigner()
logger = logging.getLogger("django")

REMEMBER_COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1 year


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



def _remembered_donor(request):
    cookie_value = request.COOKIES.get("donor_dashboard_token")
    if not cookie_value:
        return None, False # no donor found; cookie not invalid//expired
    try:
        donor_url = signer.unsign(cookie_value, max_age=REMEMBER_COOKIE_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None, True # no donor & cookie == invalid/expired
    donor = Donor.objects.filter(donor_url=donor_url).first()
    if donor is None:
        return None, True
    return donor, False # valid donor, cookei == valid!


def _attach_remember_cookie(response, donor_url):
    response.set_cookie(
        "donor_dashboard_token",
        signer.sign(donor_url),
        max_age=REMEMBER_COOKIE_MAX_AGE,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )


def donor_access_view(request):
    remembered_donor, cookie_invalid = _remembered_donor(request)
    if remembered_donor:
        auto_token = signer.sign(remembered_donor.donor_url)
        return redirect('donor_dashboard', token=auto_token)
    context = {
        "remember_me": False,
        "remember_cookie_expired": cookie_invalid,
    }
    if request.method == 'POST':
        email = request.POST.get("email", None)
        remember_me = request.POST.get("remember_me") == "on"
        context["email"] = email
        context["remember_me"] = remember_me
        if email:
            context["email"] = email
            donor = Donor.objects.filter(email=email).first()
            if not donor:
                context["error"] = "donor_not_found"
            else:
                token = signer.sign(donor.donor_url)
                access_link = reverse('donor_dashboard', kwargs={'token': token})
                if remember_me:
                    query = urllib.parse.urlencode({"remember": "1"})
                    access_link = f"{access_link}?{query}"
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
    response = render(
        request,
        'payfast/donor_access.html',
        context
    )
    if cookie_invalid:
        response.delete_cookie("donor_dashboard_token")
    return response


def donor_dashboard_view(request, token):
    try:
        donor_url = signer.unsign(token, max_age=86400)  # 24 hours in seconds
        donor = get_object_or_404(Donor, donor_url=donor_url)
        remembered_donor, cookie_invalid = _remembered_donor(request)
        remember_param = request.GET.get("remember", "").lower()
        refresh_cookie = remember_param in {"1", "true", "yes", "on"} or (
            remembered_donor and remembered_donor.id == donor.id
        )

        donor_form = DonorForm(instance=donor)
        donations = Donation.objects.filter(donor=donor).order_by("-datetime_of_donation")
        paginator = Paginator(donations, 100)
        page_number = request.GET.get('page')
        donations_page_obj = paginator.get_page(page_number)
        subscriptions = Subscription.objects.filter(donor=donor).order_by("-created_at")
        has_active_subscription = subscriptions.filter(status='active').exists()
        certificates = S18ACertificate.objects.filter(donor=donor)
        can_request_certificate = bool(S18ACertificate.available_tax_years(donor))

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
        response = render(request, 'payfast/donor_dashboard.html', {
            'donor': donor,
            'donations': donations_page_obj,
            'subscriptions': subscriptions,
            'donor_form': donor_form,
            'token': token,
            'payfast_return_url': settings.PAYFAST_RETURN_URL,
            'has_active_subscription': has_active_subscription,
            'certificates': certificates,
            'can_request_certificate': can_request_certificate,
        })
        if refresh_cookie:
            _attach_remember_cookie(response, donor.donor_url)
        elif cookie_invalid:
            response.delete_cookie("donor_dashboard_token")
        return response
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

                now = timezone.localtime(timezone.now())
                formatted_now = now.isoformat(timespec='seconds')

                pf_data = [
                    ("merchant-id", str(settings.PAYFAST_MERCHANT_ID).strip()),
                    ("passphrase", str(settings.PAYFAST_PASS_PHRASE).strip()),
                    ("timestamp", str(formatted_now).strip()),
                    ("version", "v1")
                ]
                pfParamString = ''
                for key, value in pf_data:
                    pfParamString += f"{key}={urllib.parse.quote_plus(value)}&"
                pfParamString = pfParamString[:-1]
                signature = hashlib.md5(pfParamString.encode("utf-8")).hexdigest()

                headers = {
                    "merchant-id": str(settings.PAYFAST_MERCHANT_ID).strip(),
                    "version": "v1",
                    "timestamp": str(formatted_now).strip(),
                    "signature": signature
                }
                response = requests.put(cancel_url, headers=headers)
                if response.status_code == 200:
                    subscription.status = "canceled"
                    subscription.save()
                    logger.info(f"Successfully canceled subscription {subscription.subscription_id}")
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Your subscription was canceled successfully"
                    )
                else:
                    logger.error(f"Failed to cancel subscription {subscription.subscription_id}. Status: {response.status_code} | Content: {response.content}")
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "There was an error canceling your subscription. Please try again later!"
                    )

        return redirect('donor_dashboard', token=token)
    except (BadSignature, SignatureExpired):
        logger.error("Invalid or expired token in cancel_subscription")
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
    if request.method == 'GET':
        remembered_donor, cookie_invalid = _remembered_donor(request)
        if remembered_donor:
            token = signer.sign(remembered_donor.donor_url)
            return redirect('donor_dashboard', token=token)

    default_amount = 100

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = PayfastPaymentForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            name = form.cleaned_data.get("name")
            display_name = "Anonymous" # we default to anon; let user change
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
                if not donor.display_name:
                    donor.display_name = display_name
                    donor.save()
            else:
                donor = Donor.objects.create(
                    email=email, 
                    name=name,
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
        logger.info(f"Received PayFast IPN: {data}")
        received_signature = data.get('signature', '')
        # Verify the signature
        if verify_payfast_signature(data, received_signature):
            # Process IPN data
            payment_status = data.get('payment_status')
            subscription_id = data.get('token', None)
            transaction_id = data.get('pf_payment_id')
            amount_gross = data.get('amount_gross')
            email_address = data.get('email_address')

            # Validate email address
            if not email_address:
                logger.error(f"PayFast IPN missing email_address: {data}")
                return HttpResponse(status=400)
            
            if payment_status in ['CANCELLED']:
                if subscription_id:
                    subscription = Subscription.objects.filter(
                        subscription_id=subscription_id
                    ).first()
                    
                    if subscription:
                        if payment_status == 'CANCELLED':
                            subscription.status = 'canceled'
                            logger.info(f"Subscription {subscription_id} canceled via IPN")
                        subscription.save()
                    else:
                        logger.warning(f"Received {payment_status} IPN for unknown subscription: {subscription_id}")
                
                return HttpResponse(status=200)
            donor = Donor.objects.filter(email=email_address).first()
            currency, _ = Currency.objects.get_or_create(
                currency_abr="ZAR"
            )
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
            logger.info(f"Successfully processed PayFast IPN for transaction {transaction_id}")
            return HttpResponse(status=200)
        else:
            logger.error(f"PayFast IPN signature verification failed: {data}")
            return HttpResponse(status=400)
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


def donor_dashboard_logout(request):
    response = redirect('donor_access')
    response.delete_cookie("donor_dashboard_token")
    messages.add_message(
        request,
        messages.INFO,
        "You have been logged out on this device."
    )
    return response


## S18A tax certificates

def _certificate_pdf_response(certificate, download=True):
    pdf = certificate_pdf_bytes(certificate)
    response = HttpResponse(pdf, content_type='application/pdf')
    disposition = 'attachment' if download else 'inline'
    response['Content-Disposition'] = '{}; filename="{}"'.format(
        disposition, certificate_filename(certificate))
    return response


def standard_certificate_email(certificate):
    """The standard (subject, body) for the donor email - also used to
    prefill the customisable version, so staff start from the same wording."""
    body = render_to_string('donationPage/email/certificate_email_body.txt',
                            {'certificate': certificate}).strip()
    return donation_settings.EMAIL_SUBJECT, body


def send_certificate_email(certificate, subject=None, body=None):
    """Email the certificate PDF to the donor. returns (sent, error).

    ``subject`` and ``body`` default to the standard template - the staff
    email page passes in edited text for a one-off custom message.
    """
    recipient = certificate.contact_email
    if not recipient:
        return False, "This certificate has no donor email address."
    standard_subject, standard_body = standard_certificate_email(certificate)
    subject = subject or standard_subject
    body = body or standard_body
    try:
        pdf = certificate_pdf_bytes(certificate)
        html = render_to_string('donationPage/email/certificate_email.html',
                                {'certificate': certificate, 'body': body})
        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.attach_alternative(html, "text/html")
        email.attach(certificate_filename(certificate), pdf, 'application/pdf')
        email.send()
    except Exception as e:
        try:
            logger.error("Failed to email S18A certificate %s: %s",
                         certificate.pk, e)
        except Exception:
            pass
        return False, str(e)

    certificate.mark_emailed()
    return True, ""


#  donor-facing 

def certificate_request_view(request, token):
    """Donor requests an S18A certificate for a tax year. reuses the
    signed dashboard token so there's no login needed."""
    try:
        donor_url = signer.unsign(token, max_age=86400)
    except (BadSignature, SignatureExpired):
        return HttpResponse("Invalid or expired link.", status=400)

    donor = get_object_or_404(Donor, donor_url=donor_url)
    tax_years = S18ACertificate.available_tax_years(donor)

    if not tax_years:
        messages.add_message(
            request, messages.WARNING,
            "We have no completed donations on record for you yet, so there is "
            "nothing to issue a tax certificate for.")
        return redirect('donor_dashboard', token=token)

    if request.method == 'POST':
        form = CertificateRequestForm(request.POST, instance=donor,
                                      tax_years=tax_years)
        if form.is_valid():
            # persist the SARS details back onto the donor so we can reuse them
            donor = form.save()
            year = int(form.cleaned_data['tax_year'])

            certificate = S18ACertificate(requested_by_donor=True)
            certificate.snapshot_from_donor(donor)
            donations = certificate.build_from_tax_year(donor, year)

            duplicate_of = S18ACertificate.objects.filter(
                donor=donor, tax_year=year).exclude(
                    status=S18ACertificate.STATUS_REJECTED).first()
            if duplicate_of:
                certificate.staff_notes = (
                    "Possible duplicate of certificate #{} ({}).".format(
                        duplicate_of.pk, duplicate_of.get_status_display()))

            certificate.save()
            certificate.donations.set(donations)

            _notify_staff_of_request(request, certificate, duplicate_of)
            messages.add_message(
                request, messages.SUCCESS,
                "Your tax certificate request has been submitted. Our team will "
                "review it and email your certificate once approved.")
            return redirect('donor_dashboard', token=token)
    else:
        form = CertificateRequestForm(instance=donor, tax_years=tax_years)

    return render(request, 'donationPage/certificate_request.html', {
        'form': form,
        'donor': donor,
        'token': token,
    })


def _notify_staff_of_request(request, certificate, duplicate_of=None):
    try:
        subject = "New S18A certificate request - {}".format(
            certificate.donor_name)
        if duplicate_of:
            subject = "[possible duplicate] " + subject
        message = render_to_string(
            'donationPage/email/certificate_request_staff.html',
            {'certificate': certificate,
             'duplicate_of': duplicate_of,
             'detail_url': request.build_absolute_uri(
                 certificate.get_absolute_url())})
        send_mail(subject, strip_tags(message), settings.DEFAULT_FROM_EMAIL,
                  donation_settings.STAFF_EMAILS, html_message=message)
    except Exception as e:
        logger.error("Failed to notify staff of S18A request: %s", e)


def donor_certificate_pdf(request, pk, token):
    """lets a donor download their own approved certificate, using the
    same signed dashboard token as donor_dashboard_view."""
    try:
        donor_url = signer.unsign(token, max_age=86400)
    except (BadSignature, SignatureExpired):
        return HttpResponse("Invalid or expired link.", status=400)

    donor = get_object_or_404(Donor, donor_url=donor_url)
    certificate = get_object_or_404(S18ACertificate, pk=pk, donor=donor)
    # never expose a draft - it has no receipt number yet and could still change.
    if not certificate.is_approved:
        raise Http404
    return _certificate_pdf_response(certificate, download=True)


# saff-facing

def _require_staff(request):
    if not request.user.has_perm("donationPage.change_s18acertificate"):
        raise Http404


def _requested_tax_year(request):
    """the tax_year filter as an int, or None - validated here because it
    ends up interpolated into the export's filename."""
    raw = request.GET.get('tax_year', '')
    return int(raw) if raw.isdigit() else None


def _filtered_certificates(request):
    """The certificates matching the list page's filters"""
    certificates = S18ACertificate.objects.select_related('donor')
    status = request.GET.get('status', '')
    if status:
        certificates = certificates.filter(status=status)
    year = _requested_tax_year(request)
    if year:
        certificates = certificates.filter(tax_year=year)
    query = request.GET.get('q', '').strip()
    if query:
        matches = (Q(donor_name__icontains=query)
                   | Q(surname__icontains=query)
                   | Q(contact_email__icontains=query)
                   | Q(donor__name__icontains=query)
                   | Q(donor__email__icontains=query))
        if query.isdigit():
            matches = matches | Q(receipt_number=int(query))
        certificates = certificates.filter(matches)
    return certificates


@login_required
def staff_certificate_list(request):
    _require_staff(request)
    paginator = Paginator(_filtered_certificates(request), 50)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'donationPage/staff/certificate_list.html', {
        'page_obj': page_obj,
        'status': request.GET.get('status', ''),
        'status_choices': S18ACertificate.STATUS_CHOICES,
        'q': request.GET.get('q', '').strip(),
        'tax_year': _requested_tax_year(request),
        'tax_years': S18ACertificate.objects.exclude(
            tax_year=None).values_list(
                'tax_year', flat=True).distinct().order_by('-tax_year'),
    })


@login_required
def staff_certificate_csv(request):
    """Export the filtered certificates in the SARS submission layout.

    only issued receipts get exported - a draft has no receipt number, so
    it's not something SARS has been told about anyway.
    """
    _require_staff(request)
    certificates = _filtered_certificates(request).filter(
        status__in=(S18ACertificate.STATUS_APPROVED,
                    S18ACertificate.STATUS_EMAILED),
        receipt_number__isnull=False).order_by('receipt_number')

    year = _requested_tax_year(request)
    filename = "groundup-s18a-{}.csv".format(year or "all")
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(
        filename)
    # excel only reads a csv as utf-8 if it starts with the byte-order mark.
    response.write('\ufeff')
    sars.write(certificates, response)
    return response


@login_required
def staff_certificate_create(request):
    _require_staff(request)
    # optionally prefill from an existing donor + tax year.
    donor = None
    donor_id = request.GET.get('donor')
    if donor_id:
        donor = Donor.objects.filter(pk=donor_id).first()

    if request.method == 'POST':
        form = StaffCertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save()
            # the form only gives us the donor and the period, so link the
            # covered donations here - approval is what marks them as issued.
            certificate.link_period_donations()
            messages.add_message(request, messages.SUCCESS,
                                 "Certificate created.")
            return redirect('s18a.staff.detail', pk=certificate.pk)
    else:
        if donor:
            certificate = S18ACertificate()
            certificate.snapshot_from_donor(donor)
            year = request.GET.get('tax_year')
            if year:
                certificate.build_from_tax_year(donor, int(year))
            form = StaffCertificateForm(instance=certificate)
        else:
            form = StaffCertificateForm()

    return render(request, 'donationPage/staff/certificate_form.html', {
        'form': form,
        'certificate': None,
    })


@login_required
def staff_certificate_detail(request, pk):
    _require_staff(request)
    certificate = get_object_or_404(S18ACertificate, pk=pk)
    if request.method == 'POST':
        form = StaffCertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Certificate updated.")
            return redirect('s18a.staff.detail', pk=certificate.pk)
    else:
        form = StaffCertificateForm(instance=certificate)

    # warn if the same donor already has another live certificate for this
    # tax year, so we don't end up issuing two receipts for the same donations.
    duplicates = []
    if certificate.donor_id and certificate.tax_year:
        duplicates = S18ACertificate.objects.filter(
            donor=certificate.donor, tax_year=certificate.tax_year).exclude(
                pk=certificate.pk).exclude(
                    status=S18ACertificate.STATUS_REJECTED)

    return render(request, 'donationPage/staff/certificate_detail.html', {
        'form': form,
        'certificate': certificate,
        'duplicates': duplicates,
    })


@login_required
def staff_certificate_pdf(request, pk):
    _require_staff(request)
    certificate = get_object_or_404(S18ACertificate, pk=pk)
    return _certificate_pdf_response(
        certificate, download=bool(request.GET.get('download')))


@login_required
def staff_certificate_approve(request, pk):
    _require_staff(request)
    certificate = get_object_or_404(S18ACertificate, pk=pk)
    if request.method == 'POST':
        if certificate.status == S18ACertificate.STATUS_REJECTED:
            messages.add_message(request, messages.ERROR,
                                 "Rejected certificates cannot be approved.")
        else:
            certificate.approve(request.user)
            # approving doesn't send anything - staff pick the wording and
            # send it from the "Email certificate" page.
            messages.add_message(
                request, messages.SUCCESS,
                "Certificate approved. Receipt no. {} allocated. Nothing has "
                "been sent yet — use Email to donor.".format(
                    certificate.receipt_number))
    return redirect('s18a.staff.detail', pk=pk)


@login_required
def staff_certificate_reject(request, pk):
    _require_staff(request)
    certificate = get_object_or_404(S18ACertificate, pk=pk)
    if request.method == 'POST':
        if certificate.status != S18ACertificate.STATUS_PENDING:
            messages.add_message(
                request, messages.ERROR,
                "Issued certificates cannot be rejected. They require a "
                "separate void-and-reissue workflow.")
        else:
            certificate.reject(request.POST.get('reason', ''))
            messages.add_message(request, messages.INFO, "Certificate rejected.")
    return redirect('s18a.staff.detail', pk=pk)


@login_required
def staff_certificate_email(request, pk):
    """compose and send the donor's copy.

    GET shows the standard email alongside an editable copy of it. POST
    sends either the standard template or the edited version, depending on
    which button got clicked. the PDF gets attached either way.
    """
    _require_staff(request)
    certificate = get_object_or_404(S18ACertificate, pk=pk)

    if not certificate.is_approved:
        messages.add_message(request, messages.ERROR,
                             "Approve the certificate before emailing it.")
        return redirect('s18a.staff.detail', pk=pk)

    standard_subject, standard_body = standard_certificate_email(certificate)
    form = CertificateEmailForm(initial={'subject': standard_subject,
                                         'message': standard_body})
    subject, body = standard_subject, standard_body

    def compose_page():
        return render(request, 'donationPage/staff/certificate_email.html', {
            'certificate': certificate,
            'form': form,
            'standard_subject': standard_subject,
            'standard_body': standard_body,
        })

    if request.method != 'POST':
        return compose_page()

    if request.POST.get('mode') == 'custom':
        form = CertificateEmailForm(request.POST)
        if not form.is_valid():
            return compose_page()
        subject = form.cleaned_data['subject']
        body = form.cleaned_data['message']

    sent, error = send_certificate_email(certificate, subject, body)
    if sent:
        messages.add_message(
            request, messages.SUCCESS,
            "Certificate emailed to {}.".format(certificate.contact_email))
        return redirect('s18a.staff.detail', pk=pk)

    messages.add_message(request, messages.ERROR,
                         "Could not send the certificate: {}".format(error))
    return compose_page()
