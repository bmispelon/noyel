from django.conf.urls import patterns, url

urlpatterns = patterns('noyel.kdo.views',
    url(r'^landing/$', 'landing', name='kdo-landing'),
    
    url(r'^api/search/giftee/$', 'search_giftee', name='kdo-search-giftee'),
    url(r'^api/search/friend/$', 'search_friend', name='kdo-search-friend'),
)

urlpatterns.extend(patterns('noyel.kdo.views.comment',
    url(r'^presents/(?P<pk>\d+)/comments/create/$', 'create', name='kdo-comment-create'),
    
    url(r'^comments/(?P<pk>\d+)/update/$', 'update', name='kdo-comment-update'),
    url(r'^comments/(?P<pk>\d+)/delete/$', 'delete', name='kdo-comment-delete'),

))

urlpatterns.extend(patterns('noyel.kdo.views.present',
    url(r'^presents/$', 'base_list', name='kdo-present-list'),
    url(r'^presents/create/$', 'create', name='kdo-present-create'),
    url(r'^presents/(?P<pk>\d+)/$', 'detail', name='kdo-present-detail'),
    url(r'^presents/(?P<pk>\d+)/update/$', 'update', name='kdo-present-update'),
    url(r'^presents/(?P<pk>\d+)/delete/$', 'delete', name='kdo-present-delete'),
    url(r'^presents/(?P<pk>\d+)/purchase/$', 'purchase', name='kdo-present-purchase'),
    
    
    url(r'^presents/for/(?P<giftee>.+)/$', 'list_for_giftee', name='kdo-present-list-for-giftee'),
    url(r'^presents/create/for/(?P<giftee>.+)/$', 'create_for_giftee', name='kdo-present-create-for-giftee'),
    
    
    url(r'^presents/(?P<pk>\d+)/participants/(?P<user_pk>\d+)/remove/$', 'remove_participant', name='kdo-present-remove-participant'),

))

urlpatterns.extend(patterns('noyel.kdo.views.invitation',
    url(r'^presents/(?P<pk>\d+)/participants/invite/$', 'invite_participant', name='kdo-present-invite-participant'),

    url(r'^invitations/$', 'list', name='kdo-invitation-list'),
    url(r'^invitations/redeem/$', 'redeem', name='kdo-redeem-invitation'),
    url(r'^invitations/(?P<token>\w+)/redeem/$', 'redeem_with_token', name='kdo-redeem-invitation-with-token'),
    url(r'^invitations/(?P<token>\w+)/delete/$', 'delete', name='kdo-invitation-delete'),
    url(r'^invitations/(?P<token>\w+)/re-send/$', 're_send', name='kdo-invitation-re-send'),
))
