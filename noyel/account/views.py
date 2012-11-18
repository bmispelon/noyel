from django.utils.functional import curry
from django.views import generic
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from toolbox.next import NextMixin
from toolbox.messages import MessageMixin, FormMessageMixin
from noyel.kdo.mixins import LoginRequiredMixin
from noyel.account.forms import SignupForm, ProfileUpdateForm, PasswordChangeForm


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
