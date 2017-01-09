"""groundup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles import views
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap

from newsroom.models import Article
from newsroom.models import Author
from newsroom.views import account_profile

from filebrowser.sites import site

article_dict = {
    'queryset': Article.objects.published(),
    'date_field': 'published',
}

author_dict = {
    'queryset': Author.objects.all(),
    'date_field': 'modified',
}

urlpatterns = [
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^imagegallery/', include('gallery.urls')),
    url(r'^', include('newsroom.urls')),
    url(r'^', include('payment.urls')),
    url(r'^', include('letters.urls')),

    url(r'^accounts/', include('allauth.urls')),

    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps':
         {'articles': GenericSitemap(article_dict,
                                     priority=0.5),
          'authors': GenericSitemap(author_dict,
                                    priority=0.5,
                                    changefreq='weekly'),
          'flatpages': FlatPageSitemap}},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^cache/', include('clearcache.urls', namespace="cache")),
    url(r'^404testing',
        TemplateView.as_view(template_name='404.html'),
        name='test404'),
    url(r'^500testing',
        TemplateView.as_view(template_name='500.html'),
        name='test500'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
