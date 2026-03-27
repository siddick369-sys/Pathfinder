from django.contrib import admin
from .models import MentorProfile, MentorSession, MentorReview, StudyGroup, StudyGroupMember


@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'university', 'hourly_rate_fcfa', 'average_rating', 'total_sessions', 'is_available', 'is_verified']
    list_filter = ['is_available', 'is_verified', 'university']
    search_fields = ['user__first_name', 'user__last_name', 'university']


@admin.register(MentorSession)
class MentorSessionAdmin(admin.ModelAdmin):
    list_display = ['mentee', 'mentor', 'session_type', 'date', 'status', 'price_fcfa', 'is_free_intro']
    list_filter = ['status', 'session_type', 'is_free_intro']
    date_hierarchy = 'date'


@admin.register(MentorReview)
class MentorReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'session', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'mentor', 'max_members', 'price_per_member_fcfa', 'is_active']
    list_filter = ['is_active']


@admin.register(StudyGroupMember)
class StudyGroupMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'joined_at']
