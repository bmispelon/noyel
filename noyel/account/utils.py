from django.contrib.auth.models import User

def get_friends_for_user(user, queryset=None):
    """Return a queryset of users that have participated with the given user
    on at least one present.
    
    If a queryset is passed, use that as a base.
    
    """
    # TODO: this should really be a method on the User class.
    if queryset is None:
        queryset = User.objects.all()
    return queryset.filter(present__participants=user)
