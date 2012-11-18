from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

login_required = method_decorator(login_required)


class LoginRequiredMixin(object):
    """Only logged in users can access the View."""
    @login_required
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class UserQuerysetMixin(object):
    """Override the get_queryset method to filter agains a user field."""
    user_field_name = 'user'
    def get_queryset(self):
        base = super(UserQuerysetMixin, self).get_queryset()
        return base.filter(**{self.user_field_name: self.request.user})
