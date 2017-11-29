import json

from django.db.models import Count
from django.http import HttpResponse
from django.views import generic

from noyel.kdo.mixins import LoginRequiredMixin
from noyel.kdo.models import Present, Comment
from noyel.account.utils import get_friends_for_user


class LandingView(LoginRequiredMixin, generic.TemplateView):
    """Show latest presents and comments."""
    template_name = "kdo/landing.html"
    
    def get_context_data(self, **kwargs):
        context = super(LandingView, self).get_context_data(**kwargs)
        context.update({
            'latest_presents': Present.objects.filter(
                                   participants__user=self.request.user
                               ).exclude(
                                   status=Present.STATUS.ARCHIVED,
                               ).order_by('-created_on')[:10],
            'latest_comments': Comment.objects.filter(
                                   present__participants__user=self.request.user
                               ).exclude(
                                   present__status=Present.STATUS.ARCHIVED,
                               ).order_by('-posted_on')[:10],
        })
        return context

landing = LandingView.as_view()


class GifteeSearchView(LoginRequiredMixin, generic.View): # TODO: json mixin?
    """Given a search query, return a json of a list of matching giftees."""
    
    def get(self, request):
        search = request.GET.get('q')
        qs = Present.objects.filter(participants__user=request.user,
                                    giftee__startswith=search)
        qs = qs.values('giftee').annotate(count=Count('pk'))
        l = sorted(qs, key=lambda row: row['count'], reverse=True)
        l = [row['giftee'] for row in l]
        
        return HttpResponse(json.dumps(l), mimetype='application/json')

search_giftee = GifteeSearchView.as_view()


class FriendSearchView(LoginRequiredMixin, generic.View): # TODO: json mixin
    """Return a json list of the current user's friends matchin the query."""
    
    def get(self, request):
        search = request.GET.get('q')
        qs = get_friends_for_user(request.user)
        qs = qs.filter(username__startswith=search).distinct()
        qs = qs.values_list('username', flat=True)
        
        return HttpResponse(json.dumps(list(qs)),
                            mimetype='application/json')

search_friend = FriendSearchView.as_view()
