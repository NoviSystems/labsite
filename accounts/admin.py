
from django.contrib import admin
from django.contrib.auth import models
from django.contrib.auth.admin import UserAdmin

from itng.registration.backends.invite.admin import UserInvitationAdmin


class InviteUserAdmin(UserAdmin, UserInvitationAdmin):
    pass


# Deregister the default UserAdmin and replace it with our own
admin.site.unregister(models.User)
admin.site.register(models.User, InviteUserAdmin)
