from django.contrib import admin

from noyel.account.models import EmailAddress


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'verified']
    list_filter = ['verified']

admin.site.register(EmailAddress, EmailAddressAdmin)
