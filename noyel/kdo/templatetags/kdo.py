from urlparse import urlparse

from django import template

from noyel.kdo.forms import CommentCreateForm, PresentPurchaseForm
from noyel.kdo.models import Invitation

register = template.Library()

@register.filter
def count_matching_giftee(present, user):
    """Return the number of presents that have the same giftee as the given
    present and for which the given user is a participant.
    
    """
    return present.matching_giftee(user).count()

@register.filter
def comment_form(present, user):
    """Return an instance of a CommentCreateForm for the given present and user.
    
    """
    return CommentCreateForm(present=present, user=user)

@register.filter
def purchase_form(present, user):
    """Return an instance of a PresentPurchaseForm for the given present and
    user.
    
    """
    return PresentPurchaseForm(user=user, instance=present)

@register.assignment_tag
def invitation_count(user):
    """Return the number of invitations the given user has (including expired
    ones).
    
    """
    return Invitation.objects.for_user(user).count()

@register.filter
def netloc(url):
    """Extract the domain part of a given URL.
    If the given argument is not URL, return it as is.
    
    """
    try:
        url = str(url)
    except ValueError:
        return url
    
    netloc = urlparse(url).netloc
    return netloc or url
