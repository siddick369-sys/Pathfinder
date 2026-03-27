from django.contrib import admin
from .models import WhatsAppSubscriber, MicroLesson, WhatsAppMessage, ShareableResult


@admin.register(WhatsAppSubscriber)
class WhatsAppSubscriberAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'name', 'user', 'is_active', 'is_premium', 'daily_lesson_enabled', 'created_at']
    list_filter = ['is_active', 'is_premium']
    search_fields = ['phone_number', 'name']


@admin.register(MicroLesson)
class MicroLessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'skill', 'level', 'order', 'is_active']
    list_filter = ['level', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'direction', 'message_type', 'created_at']
    list_filter = ['direction', 'message_type']
    date_hierarchy = 'created_at'


@admin.register(ShareableResult)
class ShareableResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'career_name', 'match_percentage', 'share_code', 'views_count', 'created_at']
