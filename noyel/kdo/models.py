from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import curry
from django.contrib.sites.models import get_current_site

from noyel.kdo.emails import InvitationEmail


class Present(models.Model):
    class STATUS(object):
        REJECTED = 0
        SUGGESTED = 1
        ACCEPTED = 2
        BOUGHT = 3
        
        
        choices = [
            (REJECTED, _("rejected")),
            (SUGGESTED, _("suggested")),
            (ACCEPTED, _("accepted")),
            (BOUGHT, _("bought")),
        ]
    title = models.CharField(_("title"), max_length=50)
    giftee = models.CharField(_("giftee"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    link = models.URLField(_("link"), blank=True)
    price = models.DecimalField(_("price"), max_digits=6, decimal_places=2,
                blank=True, null=True)
    status = models.PositiveIntegerField(_("status"), choices=STATUS.choices,
                default=STATUS.SUGGESTED)
    bought_by = models.ForeignKey('auth.User', verbose_name=_("bought by"),
                                  blank=True, null=True,
                                  related_name='purchased_set')
    
    created_on = models.DateTimeField(_("added on"), auto_now_add=True)
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    
    class Meta:
        verbose_name = _("present")
        verbose_name_plural = _("presents")
    
    def __unicode__(self):
        return self.title
    
    def matching_giftee(self, user=None):
        """Return a queryset of presents that have the same giftee as this one.
        If a user is passed, restrict to presents for which the user is listed
        in the participants.
        
        """
        qs = self.__class__.objects.filter(giftee__iexact=self.giftee).exclude(pk=self.pk)
        if user is not None:
            qs = qs.filter(participants=user)
        return qs
    
    def get_new_friends_for_user(self, user):
        """Return a queryset of User objects that have participated in a present
        with the given user, but that are not participating to the current one.
        
        """
        return User.objects.exclude(present=self)\
                           .filter(present__participants=user)


class Comment(models.Model):
    present = models.ForeignKey('kdo.Present', verbose_name=_('present'))
    author = models.ForeignKey('auth.User', verbose_name=_("author"))
    text = models.TextField(_("text"))
    posted_on = models.DateTimeField(_("posted on"), auto_now_add=True)
    
    def __unicode__(self):
        cutoff = 20
        if len(self.text) > cutoff:
            return u"%s..." % self.text[:cutoff]
        else:
            return self.text
    
    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        ordering = ['-posted_on']


class InvitationManager(models.Manager):
    def for_user(self, user):
        """Return invitations for the given user."""
        q = Invitation.Q_for_user(user)
        return self.get_query_set().filter(q)


class Invitation(models.Model):
    TOKEN_SIZE = 16
    token = models.CharField(_("token"), max_length=TOKEN_SIZE, primary_key=True, default=curry(get_random_string, TOKEN_SIZE))
    present = models.ForeignKey('kdo.Present', verbose_name=_("present"))
    sent_by = models.ForeignKey('auth.User', verbose_name=pgettext_lazy("invitation", "sent by"))
    sent_to = models.EmailField(pgettext_lazy("invitation", "sent to"))
    sent_on = models.DateTimeField(pgettext_lazy("invitation", "sent on"), auto_now_add=True)
    
    objects = InvitationManager()
    
    def __unicode__(self):
        return self.sent_to
    
    class Meta:
        verbose_name = _("invitation")
        verbose_name_plural = _("invitations")
        unique_together = ('present', 'sent_to')
    
    def redeem(self, user):
        present.participants.create(user=user, present=self.present)
        self.delete() # XXX good idea?
        return self.present
    
    @classmethod
    def Q_for_user(cls, user):
        emails = user.emails.filter(verified=True)\
                            .values_list('email', flat=True)
        return models.Q(sent_to__in=emails)
    
    def get_message(self, request):
        """Return a rendered InvitationEmail message with the given request."""
        site = get_current_site(request)
        return InvitationEmail().render({
            'site': site,
            'invitation': self,
            })
    
    def send_email(self, request):
        message = self.get_message(request)
        return message.send()


class Participant(models.Model):
    present = models.ForeignKey(Present, related_name='participants')
    user = models.ForeignKey('auth.User')
    
    class Meta:
        verbose_name = _("participant")
        verbose_name_plural = _("participants")
        unique_together = ('present', 'user')
