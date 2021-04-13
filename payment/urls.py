from django.conf.urls import url
from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path('invoices/', views.invoice_list, name="invoice.list"),

    path('invoices/<int:year_begin>/<int:month_begin>/'
         '<int:year_end>/<int:month_end>/<int:author>',
         views.invoice_list, name="invoice.list"),

    url(r'^invoices/([0-9]+)-([0-9]+)$', views.invoice_detail,
        name="invoice.detail"),

    url(r'^invoices/print/([0-9]+)-([0-9]+)$', views.invoice_print,
        name="invoice.print"),

    url(r'^invoices_pdf/([0-9]+)$', views.invoice_pdf,
        name="invoice.pdf"),

    path('invoices/paye/create', views.CreatePayeRequisition.as_view(),
         name='payerequisition.create'),

    url(r'^commissions/([0-9]+)$', views.commission_detail,
        name="commissions.detail"),

    url(r'^commissions/add$', views.commission_detail,
        name="commissions.detail.add"),

    url(r'^commissions/analysis$', views.commission_analysis,
        name="commissions.detail.analysis"),

]
