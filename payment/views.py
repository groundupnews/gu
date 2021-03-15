import calendar
import pdfkit
import os
from decimal import Decimal
from dateutil import relativedelta
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.db.models import F, Q, Sum
from django.forms import modelformset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import make_aware
from django.http import HttpResponse

from newsroom.models import Author

from . import forms, models, settings


'''There is business logic in this view that belongs in themodel.
TO DO: Refactor by moving filtering by year and month, and calculations
into model.
'''


@login_required
def invoice_list(request,
                 year_begin=None, month_begin=None,
                 year_end=None, month_end=None,
                 author=None):

    now = make_aware(timezone.datetime.now())
    # Set staff status
    user = request.user
    if user.is_staff and user.has_perm("payment.change_invoice"):
        staff_view = True
    else:
        staff_view = False

    # Block anyone who isn't supposed to be here
    try:
        if not user.is_authenticated:
            raise Http404
        if staff_view is False:
            if not user.author:
                raise Http404
            if author is not None and int(author) != 0:
                if author != user.author.pk:
                    raise Http404
    except: # Let's not risk any unwarranted access
        raise Http404


    # Set date fields to coherent values
    try:
        if year_begin is None:
            year_begin = now.year
        else:
            year_begin = int(year_begin)
        if month_begin is None:
            month_begin = now.month
        else:
            month_begin = int(month_begin)
            if month_begin < 1:
                raise Http404
        if year_end is None:
            year_end = now.year
        else:
            year_end = int(year_end)
        if month_end is None:
            month_end = now.month
        else:
            month_end = int(month_end)
            if month_end > 12:
                raise Http404
        year_month_begin = make_aware(timezone.datetime(year_begin, month_begin, 1))
        year_month_end = make_aware(timezone.datetime(year_end, month_end, 1))
        last_day = calendar.monthrange(year_month_end.year,
                                       year_month_end.month)[1]
        year_month_end = make_aware(timezone.datetime(year_end, month_end, last_day,
                                                      23,59,59,99))
    except:
        raise Http404


    # Extract only between start and end dates (inclusive)
    if year_month_end >= now:
        query = (Q(date_time_processed__gte=year_month_begin) & \
                 Q(date_time_processed__lte=year_month_end)) | \
                 Q(status__lt="4")
    else:
        query = (Q(date_time_processed__gte=year_month_begin) &
                 Q(date_time_processed__lte=year_month_end) &
                 Q(status="4"))

    # Show recently deleted records
    if staff_view:
        query = query | \
                (Q(created__gte=year_month_begin) &
                 Q(created__lte=year_month_end) &
                 Q(status="5"))
    else:
        query = query & Q(status__gt="-")

    # Filter author
    if staff_view:
        if author is not None and author != 0:
            author = get_object_or_404(Author, pk=author)
            query = query &  Q(author=author)
    else:     # Filter out unauthorised records
        author = get_object_or_404(Author, pk=user.author.pk)
        query = query &  Q(author=author)

    if author is None or author == 0:
        author_pk = 0
    else:
        author_pk = author.pk

    invoices = models.Invoice.objects.filter(query).select_related("author")
    total_paid = sum([i.amount_paid + i.vat_paid + i.tax_paid
                      for i in invoices if i.status == "4"])
    total_outstanding = sum([i.amount_paid + i.vat_paid + i.tax_paid
                             for i in invoices if i.status != "4"])

    if total_paid is None:
        total_paid = Decimal(0.0)
    if total_outstanding is None:
        total_outstanding = Decimal(0.0)

    total = total_paid + total_outstanding

    previous_month = year_month_begin - relativedelta.relativedelta(months=1)

    next_month = make_aware(timezone.datetime(year_month_end.year,
                                              year_month_end.month, 1) +
                 relativedelta.relativedelta(months=1))
    if next_month > now:
        next_month = None
    if invoices:
        len_invoices = len(invoices)
    else:
        len_invoices = 0

    return render(request, "payment/invoice_list.html",
                  {'invoices': invoices,
                   'len_invoices': len_invoices,
                   'total_paid': total_paid,
                   'total_outstanding': total_outstanding,
                   'total': total,
                   'from_date': year_month_begin,
                   'end_date' : year_month_end,
                   'next_month': next_month,
                   'previous_month': previous_month,
                   'latest_month': now,
                   'author': author,
                   'author_pk': author_pk,
                   'staff_view': staff_view})

def get_merge_choices(form, invoice):
    merge_invoices = models.Invoice.objects.filter(author=invoice.author).\
        exclude(pk=invoice.pk).filter(status__lt='4')
    choices = [(None, '----')] + [(str(i.pk), str(i))
                                  for i in merge_invoices]
    form.fields['merge'].choices = choices

@login_required
def invoice_detail(request, author_pk, invoice_num, print_view=False):
    user = request.user
    can_edit = False

    if not user.is_authenticated:
        raise Http404
    staff_view = False

    if user.is_staff and user.has_perm("payment.change_invoice"):
        staff_view = True
        can_edit = True
    else:
        if request.user.author is None:
            raise Http404
        if request.user.author.pk != int(author_pk):
            raise Http404
        staff_view = False

    CommissionFormSet = modelformset_factory(models.Commission,
                                             form=forms.CommissionFormset,
                                             fields=('commission_due',
                                                     'taxable',
                                                     'vatable',
                                                     'fund',
                                                     'deleted',
                                                     'split', ),
                                             extra=0)
    invoice = get_object_or_404(models.Invoice, author__pk=author_pk,
                                invoice_num=invoice_num)
    if request.method == 'POST':
        if staff_view:
            form = forms.InvoiceStaffForm(request.POST, instance=invoice)
            get_merge_choices(form, invoice)
        else:
            form = forms.InvoiceForm(request.POST, instance=invoice)

        if form.is_valid():
            invoice = form.save(commit=False)
            if "begin_button" in request.POST and invoice.status != "-":
                invoice.status = "-"
                messages.add_message(request, messages.INFO,
                                     "Status changed to UNPROCESSED")
            if "return_button" in request.POST and invoice.status != "0":
                invoice.status = "0"
                messages.add_message(request, messages.INFO,
                                     "Status changed to REPORTER MUST APPROVE")
            elif "query_button" in request.POST and invoice.status != "1":
                invoice.status = "1"
                messages.add_message(request, messages.INFO,
                                     "Status changed to QUERIED BY REPORTER")
            elif "pay_button" in request.POST and invoice.status != "2":
                invoice.status = "2"
                messages.add_message(request, messages.INFO,
                                     "Status changed to APPROVED BY REPORTER")
            elif "approve_button" in request.POST and invoice.status != "3":
                invoice.status = "3"
                messages.add_message(request, messages.INFO,
                                     "Status changed to APPROVED BY EDITOR")
            elif "paid_button" in request.POST and invoice.status != "4":
                invoice.status = "4"
                messages.add_message(request, messages.INFO,
                                     "Status changed to PAID")
            elif "delete_button" in request.POST and invoice.status != "5":
                invoice.status = "5"
                messages.add_message(request, messages.INFO,
                                     "Status changed to DELETED")
            elif "merge_button" in request.POST and invoice.status < "4":
                if form.cleaned_data['merge'] is not None:
                    merge_pk = int(form.cleaned_data['merge'])
                    from_invoice = models.Invoice.objects.get(pk=merge_pk)
                    models.Invoice.merge_invoices(from_invoice=from_invoice,
                                                   to_invoice=invoice)
                    get_merge_choices(form, invoice)
                    form.cleaned_data['merge'] = None
                    messages.add_message(request, messages.INFO,
                                         "Invoice merged with " +
                                         str(from_invoice))
            elif form.has_changed():
                messages.add_message(request, messages.INFO,
                                     "Details updated")

            # Set the requisition number and update the counter stored in Fund
            if staff_view and invoice.requisition and invoice.fund and \
               form.cleaned_data['requisition_number'] == "":
                requisition_number = invoice.fund.prefix + " " + \
                    str(invoice.fund.next_number).zfill(3)
                invoice.requisition_number = requisition_number
                invoice.fund.next_number = invoice.fund.next_number + 1
                invoice.fund.save()

            invoice.save()

            if user.has_perm("payment.change_commission"):
                commissionformset = CommissionFormSet(request.POST,
                                                      request.FILES)
                can_edit_commissions = True
                if commissionformset.is_valid():
                    commissionformset.save()
                    invoice.save()
                    messages.add_message(request, messages.INFO,
                                         "Commissions updated")
                else:
                    messages.add_message(request, messages.ERROR,
                                         "Please correct the commissions")
            else:
                can_edit_commissions = False
        else:
            messages.add_message(request, messages.ERROR,
                                 "Please make corrections")
    else:
        if staff_view:
            form = forms.InvoiceStaffForm(request.POST or None,
                                          instance=invoice)
            get_merge_choices(form, invoice)
        else:
            if invoice.status == "-" or invoice.status == "5":
                raise Http404
            form = forms.InvoiceForm(request.POST or None, instance=invoice)

    # Get commissions
    formset = None
    can_edit_commissions = False
    if staff_view:
        commissions = models.Commission.objects.for_staff().\
                      filter(invoice=invoice)
        if user.has_perm("payment.change_commission"):
            can_edit_commissions = True
            formset = CommissionFormSet(queryset=commissions)
    else:
        commissions = models.Commission.objects.for_authors().filter(invoice=invoice)

    if formset:
        commissionformset = zip(commissions, formset)
    else:
        commissionformset = zip(commissions, range(len(commissions)))

    if print_view:
        can_edit = False
        can_edit_commissions = False
        staff_view = False
    else:
        if invoice.status == "0" or invoice.status == "1":
            can_edit = True

    if invoice.author.freelancer == "c":
        description = "commission reconciliation"
    else:
        description = "invoice"

    return render(request, "payment/invoice_detail.html",
                  {'invoice': invoice,
                   'description': description,
                   'commissionformset': commissionformset,
                   'staff_view': staff_view,
                   'form': form,
                   'can_edit': can_edit,
                   'can_edit_commissions': can_edit_commissions,
                   'formset': formset,
                   'site': Site.objects.get_current(),
                   'print_view': print_view})


@login_required
def invoice_print(request, author_pk, invoice_num):
    return invoice_detail(request, author_pk, invoice_num, print_view=True)


@staff_member_required
def commission_detail(request, pk=None):
    if not request.user.has_perm("payment.change_commission"):
        raise Http404
    commission = None
    if request.method == 'POST':
        if pk:
            commission = get_object_or_404(models.Commission, pk=pk)
            form = forms.CommissionForm(request.POST, instance=commission)
        else:
            form = forms.CommissionForm(request.POST)
        if form.is_valid():
            author = form.cleaned_data['author']
            if pk is None:
                commission = form.save(commit=False)
                commission.sys_generated = False
                commission.date_generated = timezone.now()
                commission = form.save(commit=False)
                invoice = models.Invoice.get_open_invoice_for_author(author)
            else:
                current_commission = models.Commission.objects.get(pk=pk)
                if current_commission.invoice.author == author:
                    invoice = current_commission.invoice
                else:
                    invoice = models.Invoice.\
                              get_open_invoice_for_author(author)
                commission = form.save(commit=False)
            commission.invoice = invoice
            commission.save()

            pk = commission.pk
            messages.add_message(request, messages.INFO,
                                 "Commission saved")
    else:
        if pk:
            commission = models.Commission.objects.get(pk=pk)
            form = forms.CommissionForm(instance=commission)
            form.fields["author"].initial = commission.invoice.author.pk
        else:
            form = forms.CommissionForm()
            commission = None
            author_pk = request.GET.get("author", None)
            if author_pk:
                try:
                    author = get_object_or_404(Author, pk=int(author_pk))
                    form.fields["author"].initial = author.pk
                except:
                    pass
    return render(request, "payment/commission_detail.html",
                  {'form': form,
                   'pk': pk,
                   'commission': commission})

@staff_member_required
def commission_analysis(request, pk=None):
    if not request.user.has_perm("payment.change_invoice"):
        raise Http404

    commissions = pmts = None
    total_amount = total_vat = total_paye = total_due = Decimal(0.0)
    if request.method == 'POST':
        form = forms.CommissionAnalysisForm(request.POST)
        if form.is_valid():
            commissions = models.Commission.objects.filter(invoice__status="4"). \
                          select_related("fund").select_related("invoice"). \
                          select_related("invoice__author")
            descriptions = form.cleaned_data['descriptions']
            if descriptions:
                commissions = commissions.filter(description__in=descriptions)
            funds = form.cleaned_data['funds']
            if funds:
                commissions = commissions.filter(fund__in=funds)
            authors = [int(author) for author in form.cleaned_data['authors']]
            if authors:
                commissions = commissions.filter(invoice__author__in=authors)
            date_from = form.cleaned_data['date_from']
            if date_from:
                commissions = commissions.filter(date_approved__gte=date_from)
            date_to = form.cleaned_data['date_to']
            if date_to:
                commissions = commissions.filter(date_approved__lte=date_to)
            commissions = commissions.order_by('date_approved')
            pmts = [pmt.calc_payment() for pmt in commissions]
            total_amount = sum([ p[3] for p in pmts])
            total_paye = sum([ p[1] for p in pmts])
            total_vat = sum([ p[2] for p in pmts])
            total_due = sum([ p[0] for p in pmts])
    else:
        now = timezone.datetime.now()
        previous = now - relativedelta.relativedelta(months=1)
        begin = timezone.datetime(previous.year, previous.month, 1)
        last_day = calendar.monthrange(begin.year, begin.month)[1]
        end = timezone.datetime(previous.year, previous.month, last_day)
        form = forms.CommissionAnalysisForm(initial=
                                            {'date_from': begin,
                                             'date_to': end,
                                            })
    if commissions:
        len_commissions = len(commissions)
    else:
        len_commissions = 0
    return render(request, "payment/commission_analysis.html",
                  {'form': form,
                   'commissions': commissions,
                   'len_commissions': len_commissions,
                   'total_amount': total_amount,
                   'total_paye': total_paye,
                   'total_vat': total_vat,
                   'total_due': total_due})

@login_required
def invoice_pdf(request, pk):
    if not request.user.has_perm("payment.change_commission"):
        raise Http404
    invoice = models.Invoice.objects.get(pk=pk)
    html = render_to_string("payment/invoice_pdf.html",
                            {'invoice': invoice,}, request)

    filename = "-".join([invoice.requisition_number,
                         invoice.description,
                         str(invoice.author), ]) + ".pdf"
    filename = filename.replace(" ", "-")
    pdf = pdfkit.from_string(html, False, options=settings.PDF_OPTIONS)
    response =  HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    return response
