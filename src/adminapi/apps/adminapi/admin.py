from django.contrib import admin
from django.contrib.auth.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff',)
    fields = ('username', 'password', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser',)
    readonly_fields = ('password',)
    # More fields: password, is_active, last_login, date_joined, groups, user_permissions


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
