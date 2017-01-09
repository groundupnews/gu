from django.conf.urls import url
from django.core.urlresolvers import reverse

from . import views

app_name = 'cache'

urlpatterns = [
    url(r'^clearcache$', views.clear_cache, name='clearcache'),
]
