from django.urls import path

from . import views

app_name = "judgment"


urlpatterns = [
    path('judgment/', views.EventAddView.as_view(), name='event_add'),
    path('judgment/get_case/', views.get_case, name='get_case'),
    path('judgment/list/', views.EventListView.as_view(), name='list'),
    path('judgment/event_added/', views.EventAddedView.as_view(),
         name='event_added')
]
