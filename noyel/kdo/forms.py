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

    def __init__(self, *args, **kwargs):
        super(BasePresentForm, self).__init__(*args, **kwargs)
        self.fields['price'].localize = True


class PresentCreateForm(UserFormMixin, BasePresentForm):
    def save(self): # TODO: support commit=False
        present = super(PresentCreateForm, self).save()
        present.participants.create(user=self.user, present=present)
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


class FriendChoiceField(forms.ModelChoiceField):
    # TODO: docstring
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = User.objects.all()
        kwargs.setdefault('label', _("Friend"))
        super(FriendChoiceField, self).__init__(*args, **kwargs)
    
    def label_from_instance(self, instance):
        if instance.first_name:
            return u"%s (%s)" % (instance.first_name, instance.username)
        return instance.username


class PresentInvitationForm(forms.Form):
    friend = FriendChoiceField(required=False)
    email = forms.EmailField(label=_("Email"), required=False)
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.present = kwargs.pop('present')
        super(PresentInvitationForm, self).__init__(*args, **kwargs)
        friends = get_friends_for_user(self.user)\
                      .exclude(participant__present=self.present)
        self.fields['friend'].queryset = friends
    
    def clean(self):
        cleaned = self.cleaned_data
        
        if not cleaned['friend'] and not cleaned['email']:
            msg = _("Please select a friend in the list or provide an email "
                    "address.")
            raise forms.ValidationError(msg)
        
        if cleaned['friend']:
            return {'friend': cleaned['friend'], 'email': u''}
        
        assert cleaned['email']
        try:
            base_qs = self.fields['friend'].queryset
            user = base_qs.get(emails__email=cleaned['email'],
                               emails__verified=True)
        except User.DoesNotExist:
            pass
        else:
            return {'friend': user, 'email': u''}
        
        return {'friend': None, 'email': cleaned['email']}
    
    def save_invitation(self):
        email = self.cleaned_data['email']
        assert email
        return Invitation.objects.create(present=self.present,
                                         sent_by=self.user,
                                         sent_to=email,
                                         )


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


class PresentPurchaseForm(UserFormMixin, forms.ModelForm):
    class Meta:
        model = Present
        fields = ['price']
    
    def clean(self):
        if self.instance.bought_by:
            msg = _("This present has already been purchased by %(user)s.")
            raise forms.ValidationError(msg % self.instance.bought_by.username)
        return super(PresentPurchaseForm, self).clean()
    
    def save(self, commit=True):
        instance = super(PresentPurchaseForm, self).save(commit=False)
        instance.bought_by = self.user
        instance.status = Present.STATUS.BOUGHT
        if commit:
            instance.save()
        return instance
