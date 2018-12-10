from allauth.account.views import PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy


class LoginAfterPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return reverse_lazy('newsroom:user.profile')


login_after_password_change = login_required(
    LoginAfterPasswordChangeView.as_view())
