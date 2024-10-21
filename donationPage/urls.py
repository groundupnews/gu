from django.urls import path
from . import views
from .utils import cache_except_staff
from django.views.decorators.cache import cache_page
from . import  settings

urlpatterns = [
    path('donations/', views.page, name='donation.page'),
    path('<donor_url>/', views.donorDash, name='donation.dashboard'),

    path('donations/payfast/', views.payment_view, name='make_payment'),
    path('donations/payment-success/', views.payment_success, name='payment_success'),
    path('donations/payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('donations/payment-notify/', views.payfast_ipn, name='payment_notify'),
    path('donations/donor-access/', views.donor_access_view, name='donor_access'),
    path('donations/donor-dashboard/<str:token>/', views.donor_dashboard_view, name='donor_dashboard'),
    path('donations/cancel-subscription/<str:token>/', views.cancel_subscription, name='cancel_subscription'),
]
