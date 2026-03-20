from django.contrib import admin
from .models import AttendanceRecord, LeaveRequest, WorkSchedule, AttendanceSummary


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'status', 'check_in', 'check_out', 'working_hours', 'location']
    list_filter = ['status', 'date', 'location']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    date_hierarchy = 'date'
    readonly_fields = ['working_hours', 'overtime_hours', 'created_at', 'updated_at']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'leave_type', 'start_date', 'end_date', 'duration_days', 'status', 'reviewed_by']
    list_filter = ['status', 'leave_type']
    search_fields = ['user__username', 'user__first_name']
    readonly_fields = ['created_at', 'reviewed_at']
    actions = ['approve_leaves', 'reject_leaves']

    def duration_days(self, obj):
        return f'{obj.duration_days} jour(s)'
    duration_days.short_description = 'Durée'

    def approve_leaves(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='approved', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} demande(s) approuvée(s).')
    approve_leaves.short_description = '✅ Approuver les demandes sélectionnées'

    def reject_leaves(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='rejected', reviewed_by=request.user, reviewed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} demande(s) refusée(s).')
    reject_leaves.short_description = '❌ Refuser les demandes sélectionnées'


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['user', 'shift', 'start_time', 'end_time', 'effective_from', 'is_active']
    list_filter = ['shift', 'is_active']


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'present_days', 'absent_days', 'total_hours', 'attendance_rate']
    list_filter = ['year', 'month']
