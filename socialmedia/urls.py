from django.urls import path

from . import views

app_name = "socialmedia"


urlpatterns = [
    path('twitterhandle/create/', views.TwitterHandleCreate.as_view(),
         name='twitterhandle.add'),
    path('twitterhandle/update/<int:pk>/', views.TwitterHandleUpdate.as_view(),
         name='twitterhandle.update'),
    path('twitterhandle/view/<int:pk>/', views.TwitterHandleDetail.as_view(),
         name='twitterhandle.detail'),
]
