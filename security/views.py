from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from allauth.account.views import PasswordChangeView


class LoginAfterPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return reverse_lazy('user.profile')


login_after_password_change = login_required(
    LoginAfterPasswordChangeView.as_view())
