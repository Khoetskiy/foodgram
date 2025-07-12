from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = 'не задано'
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Персональная информация',
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'date_joined',
                    'last_login',
                )
            },
        ),
        (
            'Разрешения',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
    )
    readonly_fields = ('date_joined', 'last_login')
    add_fieldsets = (
        (
            None,
            {
                'classes': ('extrapretty',),  # collapse, wide, extrapretty
                'fields': (
                    'email',
                    'username',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                ),
            },
        ),
    )
    ordering = ('email',)
