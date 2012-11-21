from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import ugettext as _

from noyel.account.models import EmailAddress


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
    email = forms.EmailField(label=_("email address"), required=False)
    
    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name')
    
    def clean_email(self):
        """Check if the email already exists, raising an error if it does."""
        email = self.cleaned_data.get('email', '')
        if not email:
            return email
        try:
            EmailAddress.objects.get(email=email)
        except EmailAddress.DoesNotExist:
            return email
        raise forms.ValidationError(_("This email address is already taken."))


class ProfileUpdateForm(CleanUsernameMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name']


class EmailAddressForm(forms.ModelForm):
    class Meta:
        model = EmailAddress
        fields = ['email']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EmailAddressForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super(EmailAddressForm, self).save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance
