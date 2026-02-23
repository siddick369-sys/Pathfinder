from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'filiere', 'niveau', 'level', 'total_xp', 'global_progress')
    list_filter = ('filiere', 'niveau', 'level', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('PathFinder', {
            'fields': ('filiere', 'niveau', 'avatar_initials', 'global_progress', 'total_xp', 'level'),
        }),
    )
