from django.contrib import admin

from noyel.kdo.models import Invitation


class InvitationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Invitation, InvitationAdmin)
