from django.contrib import admin
from django.contrib.auth import models
from django.utils.translation import ugettext_lazy as _
from registration_invite.admin import UserInvitationAdmin


# copied from worklog
class DefaultYesFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
            (None, _('Yes')),
            ('no', _('No')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


class UserIsActiveFilter(DefaultYesFilter):
    title = _('active status')
    parameter_name = 'active'

    def queryset(self, request, queryset):
        if self.value() == 'all':
            return queryset.all()
        # Defaults to show Active Users when all query strings not equal to 'No' or 'All' are passed
        return queryset.filter(is_active=(self.value() != 'no'))


class ActiveUserAdmin(UserInvitationAdmin):
    list_display = UserInvitationAdmin.list_display + ('is_active', )
    list_filter = ('is_staff', 'is_superuser', UserIsActiveFilter, 'groups')


# Deregister the default UserAdmin and replace it with our own
admin.site.unregister(models.User)
admin.site.register(models.User, ActiveUserAdmin)
