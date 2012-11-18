from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.validators import validate_email

from noyel.kdo.models import Present, Comment, Invitation
from noyel.account.utils import get_friends_for_user


class UserFormMixin(object):
    """A modelform that takes a user instance in its init method."""
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(UserFormMixin, self).__init__(*args, **kwargs)


class BasePresentForm(forms.ModelForm):
    class Meta:
        model = Present
        fields = ['title', 'giftee', 'description', 'link', 'price']


class PresentCreateForm(UserFormMixin, BasePresentForm):
    def save(self): # TODO: support commit=False
        present = super(PresentCreateForm, self).save()
        present.participants.add(self.user)
        return present


class PresentUpdateForm(BasePresentForm):
    pass


class BaseCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'class': 'input-xlarge'
            }),
        }


class CommentCreateForm(UserFormMixin, BaseCommentForm):
    def __init__(self, *args, **kwargs):
        self.present = kwargs.pop('present')
        super(CommentCreateForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        comment = super(CommentCreateForm, self).save(commit=False)
        comment.author = self.user
        comment.present = self.present
        if commit:
            comment.save()
        return comment


class CommentUpdateForm(BaseCommentForm):
    pass


class PresentInvitationForm(forms.Form):
    user = forms.CharField(label=_("user"), help_text=_("Username or email"), required=True)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.present = kwargs.pop('present')
        super(PresentInvitationForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['placeholder'] = self.fields['user'].help_text
    
    def clean_user(self):
        query = self.cleaned_data['user']
        try:
            validate_email(query)
        except forms.ValidationError:
            pass
        else:
            return query
        
        try:
            user = User.objects.get(username=query)
            self.cleaned_data['user_object'] = user
        except User.DoesNotExist:
            user = None
        
        if not user or user not in get_friends_for_user(self.user):
            self.cleaned_data.pop('user_object', None) # Remove if it exists
            raise forms.ValidationError(_("User unknown. Try contacting them using their email address."))
        
        return query
    
    def save(self):
        """Create an Invitation object, save it to the database then return it.
        """
        assert not self.cleaned_data.get('user_object')
        email_address = self.cleaned_data['user']
        return Invitation.objects.create(present=self.present,
                                         sent_by=self.user,
                                         sent_to=email_address)


class RedeemInvitationForm(UserFormMixin, forms.Form):
    token = forms.CharField(label=_("token"), required=True)
    
    error_messages = {
        'invalid': _("This token is invalid."), # TODO: better explanation
    }
    
    def clean_token(self):
        token = self.cleaned_data['token']
        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid'])
        
        self.cleaned_data['invitation'] = invitation
    
    def save(self):
        """Redeem the invitation."""
        return self.cleaned_data['invitation'].redeem(self.user)
