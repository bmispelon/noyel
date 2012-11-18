from django.conf.urls import patterns, url

urlpatterns = patterns('noyel.account.views',
    url(r'^welcome/$', 'welcome', name='kdo-welcome'),
    url(r'^signup/$', 'signup', name='kdo-signup'),
    url(r'^signup/success/$', 'signup_success', name='kdo-signup-success'),
    url(r'^good-bye/$', 'logged_out', name='kdo-logged-out'),
    url(r'^login-required/$', 'login_required', name='kdo-login-required'),
    url(r'^profile/update/$', 'profile_update', name='kdo-profile-update'),
    url(r'^profile/change-password/$', 'password_update', name='kdo-password-update'),
    
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
)
