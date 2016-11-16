from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.views import generic
from django.views.generic import View
from django.db.models import Q
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.utils.html import strip_tags
from django.http import HttpResponseForbidden
from django.views.decorators.http import last_modified
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory

from . import models
from . import forms

# Create your views here.

@login_required
def invoice_list(request):
    user = request.user
    if not user.is_authenticated():
        raise Http404
    staff_view = False
    # Staff query
    if user.is_staff and user.has_perm("payment.change_invoice"):
        invoices = models.Invoice.objects.all()
        staff_view = True
    elif user.author is not None and user.author.freelancer is True:
        invoices = models.Invoice.objects.filter(author=user.author)
    else:
        raise Http404
    return render(request, "payment/invoice_list.html",
                  {'invoices': invoices,
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
                                                     'fund',),
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
            if "return_button" in request.POST and invoice.status != "0":
                invoice.status = "0"
                messages.add_message(request, messages.INFO,
                                     "Status changed to UNPAID")
                invoice.save()
            elif "query_button" in request.POST and invoice.status != "1":
                invoice.status = "1"
                messages.add_message(request, messages.INFO,
                                     "Status changed to QUERIED BY YOU")
                invoice.save()
            elif "pay_button" in request.POST and invoice.status != "2":
                invoice.status = "2"
                messages.add_message(request, messages.INFO,
                                     "Status changed to APPROVED BY YOU")
                invoice.save()
            elif "approve_button" in request.POST and invoice.status != "3":
                invoice.status = "3"
                messages.add_message(request, messages.INFO,
                                     "Status changed to APPROVED")
                invoice.save()
            elif "paid_button" in request.POST and invoice.status != "4":
                invoice.status = "4"
                messages.add_message(request, messages.INFO,
                                     "Status changed to PAID")
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
            form = forms.InvoiceStaffForm(request.POST or None, instance=invoice)
        else:
            form = forms.InvoiceForm(request.POST or None, instance=invoice)

    if invoice.status < "2":
        can_edit = True

    # Get commissions
    formset = None
    can_edit_commissions = False
    if staff_view:
        commissions = models.Commission.objects.filter(invoice=invoice)
        if user.has_perm("payment.change_commission"):
            can_edit_commissions = True
            formset = CommissionFormSet(queryset=commissions)
    else:
        commissions = models.Commission.objects.filter(invoice=invoice).\
                      filter(fund__isnull=False)
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
