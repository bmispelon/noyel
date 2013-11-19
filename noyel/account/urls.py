from django.conf.urls import patterns, url

urlpatterns = patterns('noyel.account.views',
    url(r'^welcome/$', 'welcome', name='kdo-welcome'),
    url(r'^signup/$', 'signup', name='kdo-signup'),
    url(r'^signup/success/$', 'signup_success', name='kdo-signup-success'),
    url(r'^good-bye/$', 'logged_out', name='kdo-logged-out'),
    url(r'^login-required/$', 'login_required', name='kdo-login-required'),
    url(r'^profile/update/$', 'profile_update', name='kdo-profile-update'),
    url(r'^profile/change-password/$', 'password_update', name='kdo-password-update'),
    url(r'^profile/emails/create/$', 'email_create', name='kdo-email-create'),
    url(r'^profile/emails/(?P<email>.+@.+)/delete/$', 'email_delete', name='kdo-email-delete'),
    url(r'^profile/emails/(?P<email>.+@.+)/resend/$', 'email_resend_verify_message', name='kdo-email-resend-verify-message'),
    url(r'^profile/emails/(?P<email>.+@.+)/verify/(?P<token>\w+)/$', 'email_verify', name='kdo-email-verify'),
    
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),

    url(r'^lost-password/$', 'password_reset', name='password-reset'),
    url(r'^lost-password/email-sent/$', 'password_reset_done', name='password-reset-done'),
    url(r'^lost-password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'password_reset_confirm',
        name='password-reset-confirm'),
    url(r'^lost-password/reset/done/$', 'password_reset_complete', name='password-reset-complete'),
)
