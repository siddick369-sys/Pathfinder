from django.contrib import admin
from .models import XPEvent, Badge, UserBadge, Challenge, UserChallenge, Booster, UserBooster

@admin.register(XPEvent)
class XPEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'xp_earned', 'created_at')
    list_filter = ('action',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'category', 'condition_type', 'condition_value')
    list_filter = ('category',)

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'xp_reward', 'start_date', 'end_date', 'is_active')

@admin.register(Booster)
class BoosterAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'booster_type', 'price_fcfa', 'duration_days')
    list_filter = ('booster_type',)
