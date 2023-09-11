from django.urls import reverse, re_path

from . import views

app_name = 'cache'

urlpatterns = [
    re_path(r'^clearcache$', views.clear_cache, name='clearcache'),
]
