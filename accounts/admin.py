from django.contrib import admin
from django.contrib.auth import models

from registration_invite.admin import UserInvitationAdmin


class InviteUserAdmin(UserInvitationAdmin):
    pass


# Deregister the default UserAdmin and replace it with our own
admin.site.unregister(models.User)
admin.site.register(models.User, InviteUserAdmin)
