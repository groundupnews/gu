from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.db.models import Q
from django.db.models import F, Sum
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory


from dateutil import relativedelta
import calendar

from newsroom.models import Author

from . import models
from . import forms


'''There is business logic in this view that belongs in themodel.
TO DO: Refactor by moving filtering by year and month, and calculations
into model.
'''


@login_required
def invoice_list(request, year=None, month=None, author=None):
    user = request.user
    if not user.is_authenticated():
        raise Http404
    staff_view = False
    year_month_begin = None
    next_month = None
    previous_month = None
    total_paid_for_month = None
    total_outstanding_for_month = None
    total_for_month = None
    # Staff query

    if user.is_staff and user.has_perm("payment.change_invoice"):

        if year and int(year) == 0:
            year = 0
            year_month_begin = timezone.datetime(1900, 1, 1)

        elif year is None or month is None:
            year_month_begin = timezone.now()
            year_month_begin = timezone.datetime(year_month_begin.year,
                                                 year_month_begin.month,
                                                 1)
        else:
            try:
                year_month_begin = timezone.datetime(int(year), int(month), 1)
            except:
                raise Http404
        last_day = calendar.monthrange(year_month_begin.year,
                                       year_month_begin.month)[1]
        if year == 0:
            year_month_end = timezone.datetime(5000, 1, 1)
        else:
            year_month_end = timezone.datetime(year_month_begin.year,
                                               year_month_begin.month,
                                               last_day, 23, 59, 59)

        if year == 0:
            next_month = timezone.now()
            previous_month = timezone.now() - \
                relativedelta.relativedelta(months=1)
            query = Q()
            year_month_begin = None
        else:
            next_month = year_month_begin + \
                relativedelta.relativedelta(months=1)
            previous_month = year_month_begin - \
                relativedelta.relativedelta(months=1)

            query = (Q(date_time_processed__gte=year_month_begin) &
                     Q(date_time_processed__lte=year_month_end) &
                     Q(status="4") |
                     (Q(created__gte=year_month_begin) &
                     Q(created__lte=year_month_end) &
                     Q(status="5")))
            if year_month_begin.month == timezone.now().month and \
               year_month_begin.year == timezone.now().year:
                query = query | Q(status__lte="3")

        if author is not None and int(author) is not 0:
            author = get_object_or_404(Author, pk=author)
            query = query | Q(author=author)
        else:
            author = None

        invoices = models.Invoice.objects.filter(query)
        total_paid_for_month = invoices.filter(status="4").aggregate(
            amount_paid=Sum(F('amount_paid') + F('vat_paid') +
                            F('tax_paid')))["amount_paid"]
        total_outstanding_for_month = invoices.filter(status__lt="4").\
            aggregate(amount_paid=Sum(F('amount_paid') + F('vat_paid') +
                                      F('tax_paid')))["amount_paid"]
        if total_paid_for_month is not None and \
           total_outstanding_for_month is not None:
            total_for_month = total_paid_for_month + \
                              total_outstanding_for_month
        staff_view = True
    elif user.author is not None and user.author.freelancer is True:
        invoices = models.Invoice.objects.filter(author=user.author).\
                   filter(status__gt="-").filter(status__lt="5")
    else:
        raise Http404
    return render(request, "payment/invoice_list.html",
                  {'invoices': invoices,
                   'total_paid_for_month': total_paid_for_month,
                   'total_outstanding_for_month': total_outstanding_for_month,
                   'total_for_month': total_for_month,
                   'this_month': year_month_begin,
                   'next_month': next_month,
                   'previous_month': previous_month,
                   'author': author,
                   'staff_view': staff_view})


@login_required
def invoice_detail(request, author_pk, invoice_num, print_view=False):
    user = request.user
    can_edit = False

    if not user.is_authenticated():
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
                                             fields=('commission_due',
                                                     'taxable',
                                                     'vatable',
                                                     'fund',
                                                     'deleted',),
                                             extra=0)
    invoice = get_object_or_404(models.Invoice, author__pk=author_pk,
                                invoice_num=invoice_num)
    if request.method == 'POST':
        if staff_view:
            form = forms.InvoiceStaffForm(request.POST, instance=invoice)
        else:
            form = forms.InvoiceForm(request.POST, instance=invoice)

        if form.is_valid():
            invoice = form.save(commit=False)
            if "begin_button" in request.POST and invoice.status != "-":
                invoice.status = "-"
                messages.add_message(request, messages.INFO,
                                     "Status changed to UNPROCESSED")
                invoice.save()
            if "return_button" in request.POST and invoice.status != "0":
                invoice.status = "0"
                messages.add_message(request, messages.INFO,
                                     "Status changed to REPORTER MUST APPROVE")
                invoice.save()
            elif "query_button" in request.POST and invoice.status != "1":
                invoice.status = "1"
                messages.add_message(request, messages.INFO,
                                     "Status changed to QUERIED BY REPORTER")
                invoice.save()
            elif "pay_button" in request.POST and invoice.status != "2":
                invoice.status = "2"
                messages.add_message(request, messages.INFO,
                                     "Status changed to APPROVED BY REPORTER")
                invoice.save()
            elif "approve_button" in request.POST and invoice.status != "3":
                invoice.status = "3"
                messages.add_message(request, messages.INFO,
                                     "Status changed to APPROVED BY EDITOR")
                invoice.save()
            elif "paid_button" in request.POST and invoice.status != "4":
                invoice.status = "4"
                messages.add_message(request, messages.INFO,
                                     "Status changed to PAID")
                invoice.save()
            elif "delete_button" in request.POST and invoice.status != "5":
                invoice.status = "5"
                messages.add_message(request, messages.INFO,
                                     "Status changed to DELETED")
                invoice.save()
            elif form.has_changed():
                messages.add_message(request, messages.INFO,
                                     "Details updated")
                invoice.save()
            if user.has_perm("payment.change_commission"):
                commissionformset = CommissionFormSet(request.POST,
                                                      request.FILES)
                if commissionformset.is_valid():
                    commissionformset.save()
        else:
            messages.add_message(request, messages.ERROR,
                                 "Please make corrections")
    else:
        if staff_view:
            form = forms.InvoiceStaffForm(request.POST or None,
                                          instance=invoice)
        else:
            if invoice.status == "-" or invoice.status == "5":
                raise Http404
            form = forms.InvoiceForm(request.POST or None, instance=invoice)

    if invoice.status == "0" or invoice.status == "1":
        can_edit = True

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
        commissions = models.Commission.objects.for_authors().\
                      filter(invoice=invoice)
    if formset:
        commissionformset = zip(commissions, formset)
    else:
        commissionformset = zip(commissions, range(len(commissions)))

    if print_view:
        can_edit = False
        can_edit_commissions = False
        staff_view = False

    return render(request, "payment/invoice_detail.html",
                  {'invoice': invoice,
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
