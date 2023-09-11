from django.urls import path
from . import views
from .utils import cache_except_staff
from django.views.decorators.cache import cache_page
from . import  settings

urlpatterns = [
    path('donations/', views.page, name='donation.page'),
    path('<donor_url>/', views.donorDash, name='donation.dashboard'),
]
