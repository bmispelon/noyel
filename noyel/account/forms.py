from django.core.mail import send_mail
from django import forms
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext as _

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import (UserCreationForm, PasswordChangeForm,
                                       PasswordResetForm)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site

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


class CustomPasswordResetForm(PasswordResetForm):
    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        emails = EmailAddress.objects.filter(email__iexact=email, user__is_active=True, verified=True).select_related('user')
        print('Found %d emails' % emails.count())
        for email in emails:
            user = email.user
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])

