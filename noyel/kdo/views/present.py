from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from noyel.kdo import forms as kdo_forms
from noyel.kdo.mixins import LoginRequiredMixin, UserQuerysetMixin
from noyel.kdo.models import Present, Comment

from toolbox.messages import MessageMixin, FormMessageMixin, DeleteMessageMixin
from toolbox.next import NextMixin


class ListView(LoginRequiredMixin, UserQuerysetMixin, generic.ListView):
    """List all presents the current user has access to."""
    model = Present
    user_field_name = 'participants__user'
    
    def get_queryset(self):
        base = super(ListView, self).get_queryset()
        annotated = base.annotate(count_comments=Count('comment'))
        return annotated.order_by('-updated_on')

base_list = ListView.as_view()


class ListForGifteeView(ListView):
    """List all presents that the current user has access to and which match
    the giftee's name captured in the URL.
    
    """
    template_name = 'kdo/present_list_for_giftee.html'
    
    def get_queryset(self):
        base = super(ListForGifteeView, self).get_queryset()
        return base.filter(giftee__iexact=self.kwargs['giftee'])
    
    def get_context_data(self, **kwargs):
        context = super(ListForGifteeView, self).get_context_data(**kwargs)
        context['giftee'] = self.kwargs['giftee']
        return context

list_for_giftee = ListForGifteeView.as_view()


class ListSimilarView(ListView):
    """List present similar to the given one.
    For now, similarity means having the same giftee.
    
    """
    # TODO: custom template
    def get_queryset(self):
        base = super(ListSimilarView, self).get_queryset()
        return base.exclude(pk=self.present.pk).filter(giftee__iexact=self.present.giftee)
    
    def get(self, request, *args, **kwargs):
        self.present = get_object_or_404(Present, pk=kwargs['pk'])
        return super(ListSimilarView, self).get(request, *args, **kwargs)

list_similar = ListSimilarView.as_view()


class DetailView(LoginRequiredMixin, UserQuerysetMixin, generic.DetailView):
    """Show detail for a given present. Only accessible to users in the
    `participants` field.
    
    """
    template_name = 'kdo/present_detail.html'
    model = Present
    user_field_name = 'participants__user'

detail = DetailView.as_view()


class CreateView(LoginRequiredMixin, NextMixin, FormMessageMixin, generic.CreateView):
    """Create a present. The current user is automatically added to the
    `participants` field.
    
    """
    template_name = 'kdo/present_create.html'
    model = Present
    form_class = kdo_forms.PresentCreateForm
    default_next_url = reverse_lazy('kdo-present-list')
    form_valid_message = _("The present has been created successfully.")
    
    def get_form_kwargs(self):
        """Add the current user to the form's kwargs."""
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

create = CreateView.as_view()


class CreateForGifteeView(CreateView):
    """Create a present with the giftee field set to the name captured in the URL."""
    def get_initial(self):
        return {'giftee': self.kwargs['giftee']}
    
    def get_context_data(self, **kwargs):
        context = super(CreateForGifteeView, self).get_context_data(**kwargs)
        context['giftee'] = self.kwargs['giftee']
        return context

create_for_giftee = CreateForGifteeView.as_view()


class UpdateView(LoginRequiredMixin, UserQuerysetMixin, NextMixin, FormMessageMixin, generic.UpdateView):
    """Update a present. Only available if the current user is part of the
    `participants` field.
    
    """
    template_name = 'kdo/present_update.html'
    model = Present
    form_class = kdo_forms.PresentUpdateForm
    user_field_name = 'participants__user'
    
    form_valid_message = _("The present has been updated successfully.")
    @property
    def default_next_url(self):
        return reverse('kdo-present-detail', args=[self.object.pk])

update = UpdateView.as_view()


class DeleteView(LoginRequiredMixin, UserQuerysetMixin, NextMixin, DeleteMessageMixin, generic.DeleteView):
    """Delete a present. Only available if the current user is part of the
    `availabl_to` field.
    
    """
    model = Present
    user_field_name = 'participants__user'
    default_next_url = reverse_lazy('kdo-present-list')
    delete_message = _("The present has been deleted successfully.")

delete = DeleteView.as_view()


class RemoveParticipantView(LoginRequiredMixin, NextMixin, MessageMixin, generic.View):
    """Remove a user from a present's `participants` field.
    Throw a 404 if the user is not present in the field.
    
    """
    
    @property
    def default_next_url(self):
        return reverse('kdo-present-detail', args=[self.present.pk])
    
    def post(self, request, *args, **kwargs):
        self.present = get_object_or_404(Present, pk=kwargs['pk'],
                                         participants=request.user)
        self.user = get_object_or_404(User, pk=kwargs['user_pk'],
                                      present=self.present)
        self.present.participants.filter(user=self.user).delete()
        msg = _("The user has been removed from the present's participants "
                "successfully.")
        self.messages.success(msg)
        
        return self.redirect()

remove_participant = RemoveParticipantView.as_view()


class PurchaseView(LoginRequiredMixin, UserQuerysetMixin, NextMixin, MessageMixin, generic.UpdateView):
    """Mark the current user as having purchased the given present."""
    template_name = 'kdo/present_purchase.html'
    model = Present
    form_class = kdo_forms.PresentPurchaseForm
    user_field_name = 'participants__user'
    default_next_url = reverse_lazy('kdo-present-list')
    form_valid_message = _("You have been marked as the buyer of this present "
                           "successfully.")
    
    @property
    def default_next_url(self):
        return reverse('kdo-present-detail', args=[self.object.pk])
    
    def get_form_kwargs(self):
        kwargs = super(PurchaseView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

purchase = PurchaseView.as_view()
