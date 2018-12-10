from django.conf.urls import url
from .views import LoginAfterPasswordChangeView

app_name = 'security'

urlpatterns = [
    url(r'^accounts/password/change/$', LoginAfterPasswordChangeView.as_view(),
        name='account_change_password'),
]
