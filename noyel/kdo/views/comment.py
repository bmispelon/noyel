from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from noyel.kdo.forms import CommentCreateForm, CommentUpdateForm
from noyel.kdo.mixins import LoginRequiredMixin, UserQuerysetMixin
from noyel.kdo.models import Present, Comment

from toolbox.messages import FormMessageMixin, DeleteMessageMixin
from toolbox.next import NextMixin


class CreateView(LoginRequiredMixin, NextMixin, FormMessageMixin, generic.CreateView):
    """Add a comment to the given present."""
    model = Comment
    form_class = CommentCreateForm
    form_valid_message = _("The comment has been created successfully.")
    
    @property
    def default_next_url(self):
        return reverse('kdo-present-detail', args=[self.present.pk])
    
    def get_form_kwargs(self):
        """Add the current user to the form's kwargs."""
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['present'] = self.present
        return kwargs
    
    def dispatch(self, request, *args, **kwargs):
        self.present = get_object_or_404(Present, pk=kwargs['pk'],
                                         participants__user=request.user)
        return super(CreateView, self).dispatch(request, *args, **kwargs)

create = CreateView.as_view()


class UpdateView(LoginRequiredMixin, UserQuerysetMixin, NextMixin, FormMessageMixin, generic.UpdateView):
    """Update the given comment. Only available if the user if the comment's
    author.
    
    """
    model = Comment
    form_class = CommentUpdateForm
    user_field_name = 'author'
    form_valid_message = _("The comment has been updated successfully.")
    
    @property
    def default_next_url(self):
        return reverse('kdo-present-detail', args=[self.object.present.pk])

update = UpdateView.as_view()


class DeleteView(LoginRequiredMixin, UserQuerysetMixin, NextMixin, DeleteMessageMixin, generic.DeleteView):
    """Delete the given comment, but only if the current user is the comments's
    author.
    
    """
    model = Comment
    user_field_name = 'author'
    delete_message = _("The comment has been deleted successfully.")
    
    @property
    def default_next_url(self):
        return reverse('kdo-present-detail', args=[self.object.present.pk])

delete = DeleteView.as_view()
