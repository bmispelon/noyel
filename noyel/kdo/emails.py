from django.utils.translation import ugettext as _, get_language
from django.conf import settings

from toolbox.emails import EmailTemplate


class InvitationEmail(EmailTemplate):
    """An email containing a link to redeem an invitation, allowing a user
    to be added to the participants of a present.
    
    """
    @property # XXX: A property is needed because lazy objects dont work here
    def subject_template(self):
        return _("[{{ site.domain }}] Invitation to participate")
    
    from_email = settings.DEFAULT_FROM_EMAIL
    to_template = '{{ invitation.sent_to }}'
    
    @property
    def body_template_name(self):
        """Return the template name corresponding to the active language."""
        return 'kdo/emails/invite_%s.txt' % get_language()
