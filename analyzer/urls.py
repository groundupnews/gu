from django.urls import path

from . import views

app_name = "analyzer"

urlpatterns = [
    path('top_urls/', views.top_urls, name="top_urls")
]
