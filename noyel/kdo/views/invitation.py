from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.contrib.sites.models import get_current_site
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from noyel.kdo import forms as kdo_forms
from noyel.kdo.mixins import LoginRequiredMixin
from noyel.kdo.models import Present, Invitation
from noyel.kdo.emails import InvitationEmail

from toolbox.messages import MessageMixin, FormMessageMixin
from toolbox.next import NextMixin


class InviteParticipantView(LoginRequiredMixin, NextMixin, MessageMixin, generic.FormView):
    """Invite a participant to a present.
    If a username is given and that the corresponding user is a friend of the
    current one, then it is immediately added to the present's participants list.
    
    If an email is given, then a message is sent to that address with a unique
    link that will allow the user who receives it to be added to the present's
    participants list.
    
    """
    template_name = 'kdo/invite_participant.html'
    form_class = kdo_forms.PresentInvitationForm
    
    @property
    def default_next_url(self):
        return reverse('kdo-present-detail', args=[self.present.pk])
    
    def dispatch(self, request, *args, **kwargs):
        self.present = get_object_or_404(Present, pk=kwargs['pk'])
        return super(InviteParticipantView, self).dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super(InviteParticipantView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['present'] = self.present
        return kwargs
    
    def form_valid(self, form):
        user = form.cleaned_data.get('user_object', None)
        if user:
            msg = _("The user has been added to the present's participants successfully.")
            self.present.participants.add(user)
        else:
            msg = _("An email has been sent to the user inviting them to participate to this present.")
            try:
                invitation = form.save()
            except IntegrityError: # invitation already sent
                msg = _("The user \"%(email_address)s\" has already been invited to this present.")
                self.messages.error(msg % {'email_address': form.cleaned_data['user']})
                return self.form_invalid(form)
            self.send_invitation(invitation)
        
        self.messages.success(msg)
        return super(InviteParticipantView, self).form_valid(form)
    
    def send_invitation(self, invitation):
        site = get_current_site(self.request)
        message = InvitationEmail().render({'site': site, 'invitation': invitation})
        
        message.send()

invite_participant = InviteParticipantView.as_view()


class RedeemView(LoginRequiredMixin, FormMessageMixin, generic.FormView):
    """Prompt for a token then redeem the corresponding invitation."""
    template_name = 'kdo/redeem_invitation.html'
    form_class = kdo_forms.RedeemInvitationForm
    form_valid_message = _("The invitation has been redeemed successfully.")
    
    def get_success_url(self):
        return reverse('kdo-present-detail', args=(self.present.pk,))
    
    def get_form_kwargs(self):
        kwargs = super(RedeemView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        self.present = form.save()
        return super(RedeemView, self).form_valid(form)

redeem = RedeemView.as_view()


class RedeemWithTokenView(RedeemView):
    """Redeem the invitation correponding to the token given in the URL."""
    def get_initial(self):
        return self.kwargs

redeem_with_token = RedeemWithTokenView.as_view()


class ListView(LoginRequiredMixin, generic.ListView):
    """List pending invitations for the current user (ie those sent to the
    user's registered email address).
    
    """
    template_name = 'kdo/invitation_list.html'
    model = Invitation
    
    def get_queryset(self):
        base = super(ListView, self).get_queryset()
        base = base.filter(sent_to=self.request.user.email)
        return base.select_related('present', 'sent_by').order_by('sent_on')

list = ListView.as_view()
