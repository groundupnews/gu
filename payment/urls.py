from django.urls import path, re_path

from . import views

app_name = "payments"

urlpatterns = [
    path('invoices/', views.invoice_list, name="invoice.list"),

    path('invoices/<int:year_begin>/<int:month_begin>/'
         '<int:year_end>/<int:month_end>/<int:author>/',
         views.invoice_list, name="invoice.list"),

    re_path(r'^invoices/([0-9]+)-([0-9]+)$', views.invoice_detail,
        name="invoice.detail"),

    re_path(r'^invoices/print/([0-9]+)-([0-9]+)$', views.invoice_print,
        name="invoice.print"),

    re_path(r'^invoices_pdf/([0-9]+)$', views.invoice_pdf,
        name="invoice.pdf"),

    path('invoices/paye/create', views.CreatePayeRequisition.as_view(),
         name='payerequisition.create'),

    re_path(r'^commissions/([0-9]+)$', views.commission_detail,
        name="commissions.detail"),

    re_path(r'^commissions/add$', views.commission_detail,
        name="commissions.detail.add"),

    re_path(r'^commissions/analysis$', views.commission_analysis,
        name="commissions.detail.analysis"),

]
