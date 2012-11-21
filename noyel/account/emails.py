from django.utils.translation import ugettext as _, get_language
from django.conf import settings

from toolbox.emails import EmailTemplate


class EmailVerificationEmail(EmailTemplate):
    # TODO: docstring
    @property # XXX: A property is needed because lazy objects dont work here
    def subject_template(self):
        return _("[{{ site.domain }}] Email verification")
    
    from_email = settings.DEFAULT_FROM_EMAIL
    to_template = '{{ email.email }}'
    
    @property
    def body_template_name(self):
        """Return the template name corresponding to the active language."""
        return 'account/emails/verify_%s.txt' % get_language()
