from django.urls import path
from . import views
from .utils import cache_except_staff
from django.views.decorators.cache import cache_page
from . import  settings

urlpatterns = [
    path('donations/', views.page, name='donation.page'),
    path('<donor_url>/', views.donorDash, name='donation.dashboard'),

    path('donations/payfast/', views.payment_view, name='make_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment-notify/', views.payment_notify, name='payment_notify'),
]
