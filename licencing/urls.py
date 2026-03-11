from django.urls import path

from . import views

app_name = "licencing"


urlpatterns = [
    path("licencing/list/", views.LicenceList.as_view(), name="list"),
    path("licencing/detail/<int:pk>/", views.LicenceDetail.as_view(), name="detail"),
]
