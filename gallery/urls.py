from django.urls import re_path
from . import views
from . import feeds

app_name = "gallery"

urlpatterns = [
    re_path(r'^$', views.gallery_front, name='gallery.front'),
    re_path(r'^albums/$', views.album_list, name='album.list'),
    re_path(r'^album/([0-9]+)/$', views.album_detail, name='album.detail'),
    re_path(r'^photos/$', views.photo_list, name='photo.list'),
    re_path(r'^photos/([-\s\w]+)/$', views.photo_list, name='photo.list'),
    re_path(r'^photo/([0-9]+)/$', views.photo_detail, name='photo.detail'),
    re_path(r'^siteimages/all/rss/$', feeds.LatestPhotosRssFeed()),
    re_path(r'^siteimages/all/atom/$', feeds.LatestPhotosAtomFeed()),
    re_path(r'^siteimages/featured/rss/$', feeds.LatestFeaturedPhotosRssFeed()),
    re_path(r'^siteimages/featured/atom/$', feeds.LatestFeaturedPhotosAtomFeed()),
]
