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

from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.views.generic.base import RedirectView

from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.flatpages import views

from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap

from newsroom.models import Article
from newsroom.models import Author
from newsroom.sitemap import ArticleSitemap

from gallery.models import Photograph

from groundup.filebrowser import site

from ajax_select import urls as ajax_select_urls

article_dict = {
    "queryset": Article.objects.published(),
    "date_field": "published",
}

author_dict = {
    "queryset": Author.objects.all(),
    "date_field": "modified",
}

photo_dict = {
    "queryset": Photograph.objects.all(),
    "date_field": "modified",
}

app_name = "groundup"

urlpatterns = (
    [
        path("admin/filebrowser/", site.urls),
        path("grappelli/", include("grappelli.urls")),
        re_path(r"^ajax_select/", include(ajax_select_urls)),
        path("admin/login/", RedirectView.as_view(url="/accounts/login/")),
        path("donate/", RedirectView.as_view(url="/donation/payfast/", permanent=True)),
        path("admin/", admin.site.urls),
        path("imagegallery/", include("gallery.urls")),
        path("", include("newsroom.urls")),
        path("", include("payment.urls")),
        path("", include("letters.urls")),
        path("", include("agony.urls")),
        path("", include("socialmedia.urls")),
        path("", include("target.urls")),
        # path('', include('judgment.urls')),
        path("", include("sudoku.urls")),
        path("", include("analyzer.urls")),
        path("", include("security.urls")),
        path("", include("allauth_2fa.urls")),
        path("donation/", include("donationPage.urls")),
        path("accounts/", include("allauth.urls")),
        path(
            "sitemap.xml",
            sitemap,
            {
                "sitemaps": {
                    "articles": ArticleSitemap,
                    "authors": GenericSitemap(
                        author_dict, priority=0.5, changefreq="weekly"
                    ),
                    "photos": GenericSitemap(
                        photo_dict, priority=0.5, changefreq="daily"
                    ),
                    "flatpages": FlatPageSitemap,
                }
            },
            name="django.contrib.sitemaps.views.sitemap",
        ),
        path("cache/", include("clearcache.urls", namespace="cache")),
        re_path(
            r"^robots\.txt",
            TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
            name="robots.txt",
        ),
        re_path(
            r"^404testing",
            TemplateView.as_view(template_name="404.html"),
            name="test404",
        ),
        re_path(
            r"^500testing",
            TemplateView.as_view(template_name="500.html"),
            name="test500",
        ),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)


# handler404 = 'newsroom.views.handler404'

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

urlpatterns += [
    re_path(r"^(?P<url>.*/)$", views.flatpage),
]
