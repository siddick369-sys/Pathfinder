from django.contrib import admin
from .models import Skill, SkillResource, UserSkillProgress, UserResourceProgress


class ResourceInline(admin.TabularInline):
    model = SkillResource
    extra = 1
    fields = ('title', 'resource_type', 'level', 'url', 'file', 'duration_minutes', 'xp_reward', 'order', 'is_free_preview')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_premium', 'price_fcfa')
    list_filter = ('is_premium',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ResourceInline]


@admin.register(SkillResource)
class SkillResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'skill', 'resource_type', 'level', 'duration_minutes', 'xp_reward', 'order')
    list_filter = ('resource_type', 'level', 'skill')
    search_fields = ('title', 'description')
    list_editable = ('order', 'xp_reward')


@admin.register(UserSkillProgress)
class UserSkillProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'current_level', 'progress_percent', 'unlocked')
    list_filter = ('skill', 'unlocked')


@admin.register(UserResourceProgress)
class UserResourceProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'resource', 'completed', 'completed_at')
    list_filter = ('completed', 'resource__skill')
