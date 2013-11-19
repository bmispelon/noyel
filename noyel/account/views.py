from django.utils.functional import curry
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import views as auth_views
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import transaction

from toolbox.next import NextMixin
from toolbox.messages import MessageMixin, FormMessageMixin, DeleteMessageMixin
from noyel.kdo.mixins import LoginRequiredMixin, UserQuerysetMixin
from noyel.account.models import EmailAddress
from noyel.account.forms import (SignupForm, ProfileUpdateForm,
                                 PasswordChangeForm, EmailAddressForm,
                                 CustomPasswordResetForm)
from noyel.account.emails import EmailVerificationEmail


class WelcomeView(generic.TemplateView):
    """The landing page for anonymous users.
    Shows a paragraph explaining what the site is about and a link to sign up.
    
    """
    template_name = 'account/welcome.html'

welcome = WelcomeView.as_view()


class SignupView(generic.CreateView):
    """Create a user account on the site."""
    template_name = 'account/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('kdo-signup-success')
    
    @transaction.commit_on_success
    def form_valid(self, form):
        response = super(SignupView, self).form_valid(form) # creates self.object
        email = form.cleaned_data['email']
        if email:
            EmailAddress.objects.create(user=self.object, email=email)
            # TODO: send email verification email
        return response

signup = SignupView.as_view()


class SignupSuccessView(generic.TemplateView):
    """Success page for the signup process with a prompt to log in."""
    template_name = 'account/signup_success.html'

signup_success = SignupSuccessView.as_view()


class LoggedOutView(generic.TemplateView):
    """The page where users arrive after they log out."""
    template_name = 'account/logged_out.html'

logged_out = LoggedOutView.as_view()

login = auth_views.login
logout = curry(auth_views.logout, next_page=reverse_lazy('kdo-logged-out'))


class LoginRequiredView(generic.TemplateView):
    """The page where users arrive if they try to access a restricted page
    without being logged in.
    
    """
    template_name = 'account/login_required.html'

login_required = LoginRequiredView.as_view()


class ProfileUpdateView(LoginRequiredMixin, NextMixin, FormMessageMixin, generic.UpdateView):
    """Update the current user's profile (first name, email address)."""
    template_name = 'account/profile_update.html'
    form_class = ProfileUpdateForm
    default_next_url = reverse_lazy('kdo-landing')
    form_valid_message = _("Your profile has been updated successfully.")
    
    def get_object(self, queryset=None):
        return self.request.user

profile_update = ProfileUpdateView.as_view()


class PasswordUpdateView(LoginRequiredMixin, NextMixin , FormMessageMixin, generic.FormView):
    """Update the current user's password."""
    template_name = 'account/password_update.html'
    form_class = PasswordChangeForm
    default_next_url = reverse_lazy('kdo-profile-update')
    form_valid_message = _("Your password has been changed successfully.")
    
    def get_form_kwargs(self):
        kwargs = super(PasswordUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        self.object = form.save()
        return super(PasswordUpdateView, self).form_valid(form)

password_update = PasswordUpdateView.as_view()


class EmailCreateView(LoginRequiredMixin, NextMixin, FormMessageMixin, generic.CreateView):
    """Create an EmailAddress for the current user."""
    template_name = 'baseform.html' # TODO
    form_class = EmailAddressForm
    default_next_url = reverse_lazy('kdo-profile-update')
    form_valid_message = _("Your new email address has been created. "
                           "You should receive an message soon with a link to "
                           "verify the address belongs to you.")
    
    def get_form_kwargs(self):
        kwargs = super(EmailCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        # create self.object
        response = super(EmailCreateView, self).form_valid(form)
        self.send_email(self.object)
        return response
    
    def send_email(self, email_address):
        template = EmailVerificationEmail()
        message = template.render({'user': self.request.user,
                                   'email': email_address,
                                   'site': get_current_site(self.request)})
        return message.send()

email_create = EmailCreateView.as_view()


class EmailDeleteView(LoginRequiredMixin, UserQuerysetMixin, NextMixin, DeleteMessageMixin, generic.DeleteView):
    """Delete the given email, but only if it belongs to the current user."""
    template_name = "basedelete.html" # TODO
    model = EmailAddress
    slug_field = 'email'
    slug_url_kwarg = 'email'

email_delete = EmailDeleteView.as_view()


class EmailResendVerifyMessageView(LoginRequiredMixin, UserQuerysetMixin, NextMixin, MessageMixin, generic.DetailView):
    """Resend the email message that contains a link to verify the given email 
    address.
    
    """
    template_name = "account/email_resend_verify.html"
    model = EmailAddress
    slug_field = 'email'
    slug_url_kwarg = 'email'
    
    def get_queryset(self):
        base = super(EmailResendVerifyMessageView, self).get_queryset()
        return base.filter(verified=False)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.send_email(self.object)
        msg = _("We've resent the email. Let's hope you get it this time.")
        self.messages.success(msg)
        return self.redirect()
    
    def send_email(self, email_address):
        template = EmailVerificationEmail()
        message = template.render({'user': self.request.user,
                                   'email': email_address,
                                   'site': get_current_site(self.request)})
        return message.send()

email_resend_verify_message = EmailResendVerifyMessageView.as_view()


class EmailVerifyView(LoginRequiredMixin, UserQuerysetMixin, NextMixin, MessageMixin, generic.DetailView):
    """Verify that the current user really owns the provided email address."""
    template_name = "account/email_verify.html"
    model = EmailAddress
    slug_field = 'email'
    slug_url_kwarg = 'email'
    default_next_url = reverse_lazy('kdo-profile-update')
    
    def get_queryset(self):
        base = super(EmailVerifyView, self).get_queryset()
        return base.filter(verified=False)
    
    def get_context_data(self, **kwargs):
        context = super(EmailVerifyView, self).get_context_data(**kwargs)
        context['token'] = self.kwargs['token']
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        token = self.kwargs['token']
        if self.object.make_hash() == token:
            return self.token_valid(token)
        else:
            return self.token_invalid(token)
    
    @transaction.commit_on_success
    def token_valid(self, token):
        self.object.verified = True
        self.object.verified_on = timezone.now()
        self.object.save()
        msg = _("%(email)s has been verified successfully.")
        self.messages.success(msg % {'email': self.object.email})
        return self.redirect()
    
    def token_invalid(self, token):
        msg = _("Invalid token.")
        self.messages.error(msg)
        return self.redirect()

email_verify = EmailVerifyView.as_view()


password_reset = curry(auth_views.password_reset,
                       password_reset_form=CustomPasswordResetForm,
                       post_reset_redirect=reverse_lazy('password-reset-done'))
password_reset_done = auth_views.password_reset_done
password_reset_confirm = curry(auth_views.password_reset_confirm,
                               post_reset_redirect=reverse_lazy('password-reset-complete'))
password_reset_complete = auth_views.password_reset_complete
