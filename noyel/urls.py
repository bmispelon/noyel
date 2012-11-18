from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.shortcuts import redirect as _redirect
from noyel.kdo.urls import urlpatterns as kdo_patterns
from noyel.account.urls import urlpatterns as account_patterns

admin.autodiscover()

def redirect(to, *args, **kwargs):
    """Return a view (callable) that can be used as the second parameter to the
    url function.
    That view will permanently redirect to the given URL.
    The given parameters will be passed as-is to the shortcuts.redirect function.
    
    """
    def view(request):
        return _redirect(to, *args, permanent=True, **kwargs)
    return view

urlpatterns = patterns('',
    url(r'^$', redirect('kdo-welcome')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

urlpatterns.extend(kdo_patterns)
urlpatterns.extend(account_patterns)
