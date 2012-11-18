from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import ugettext as _


class CleanUsernameMixin(object):
    """Provide a clean_username method that rejects usernames containing @."""
    def clean_username(self):
        """Disallow @ in usernames."""
        username = self.cleaned_data['username']
        if '@' in username:
            error = _("Your username cannot contain a \"@\".")
            raise forms.ValidationError(error)
        try:
            return super(CleanUsernameMixin, self).clean_username()
        except AttributeError:
            return username


class SignupForm(CleanUsernameMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'email')


class ProfileUpdateForm(CleanUsernameMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
