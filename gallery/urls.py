from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^albums/$', views.album_list, name='album.list'),
    url(r'^album/([0-9]+)/$', views.album_detail, name='album.detail'),
    url(r'^photos/$', views.photo_list, name='photo.list'),
    url(r'^photos/([-\s\w]+)/$', views.photo_list, name='photo.list'),
    url(r'^photo/([0-9]+)/$', views.photo_detail, name='photo.detail'),
]
