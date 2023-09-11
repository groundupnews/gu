from django.urls import re_path
from .views import LoginAfterPasswordChangeView

app_name = 'security'

urlpatterns = [
    re_path(r'^accounts/password/change/$', LoginAfterPasswordChangeView.as_view(),
        name='account_change_password'),
]
