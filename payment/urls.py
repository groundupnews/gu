from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^invoices/$', views.invoice_list,
        name="invoice.list"),

    url(r'^invoices/([0-9]+)-([0-9]+)$', views.invoice_detail,
        name="invoice.detail"),

    url(r'^invoices/print/([0-9]+)-([0-9]+)$', views.invoice_print,
        name="invoice.print"),
]
