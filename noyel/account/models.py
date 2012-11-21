from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import salted_hmac, constant_time_compare

hash_key = 'noyel.account.models.EmailAddress'


class EmailAddress(models.Model):
    user = models.ForeignKey('auth.User', verbose_name=_("user"),
                             related_name='emails')
    email = models.EmailField(_("email address"), unique=True)
    verified = models.BooleanField(_("verified"), default=False)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    verified_on = models.DateTimeField(_("verified on"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")
        ordering = ['created_on']
    
    def __unicode__(self):
        return self.email
    
    def make_hash(self):
        return salted_hmac(hash_key, self.email).hexdigest()[::2]
    
    def matches_hash(self, hash):
        expected = self.make_hash()
        return constant_time_compare(expected, hash)
