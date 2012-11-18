from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import ugettext as _


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'email')
    
    def clean_username(self):
        """Disallow @ in usernames."""
        if '@' in self.cleaned_data['username']:
            raise forms.ValidationError(_("Your username cannot contain a \"@\"."))
        return super(SignupForm, self).clean_user()


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']
