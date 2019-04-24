from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        self.request.session.set_expiry(300)
        super(LoginForm, self).confirm_login_allowed(user)