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
)
