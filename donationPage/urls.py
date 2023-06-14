from django.urls import path
from . import views
from django.conf.urls import url
from .utils import cache_except_staff
from django.views.decorators.cache import cache_page
from . import  settings

urlpatterns = [
    path('donations/', views.page, name='page'),
    path('<donor_url>', views.donorDash, name='dashboard'),
]
