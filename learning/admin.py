from django.contrib import admin
from .models import (
    Department, TrainingModule, Course, Lesson, Quiz, QuizQuestion,
    QuizChoice, Enrollment, LessonProgress, QuizAttempt, Certificate
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'code', 'head_name']
    search_fields = ['name', 'code']


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    fields = ['title', 'order', 'duration_minutes', 'instructor_name', 'is_published']


@admin.register(TrainingModule)
class TrainingModuleAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'department', 'level', 'status', 'is_mandatory', 'get_enrolled_count']
    list_filter = ['level', 'status', 'department', 'is_mandatory']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseInline]

    def get_enrolled_count(self, obj):
        return obj.enrollments.count()
    get_enrolled_count.short_description = 'Inscrits'


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ['title', 'lesson_type', 'order', 'duration_minutes']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'instructor_name', 'is_published']
    list_filter = ['module', 'is_published']
    search_fields = ['title', 'instructor_name']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_type', 'order', 'duration_minutes', 'xp_reward']
    list_filter = ['lesson_type', 'course__module']
    search_fields = ['title', 'content']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'status', 'progress_percent', 'enrolled_at', 'last_activity']
    list_filter = ['status', 'module']
    search_fields = ['user__username', 'user__first_name', 'module__title']
    readonly_fields = ['progress_percent', 'enrolled_at', 'last_activity']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'completed_at', 'time_spent_minutes']
    list_filter = ['completed', 'lesson__course__module']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'user', 'module', 'score', 'issued_at', 'is_valid']
    list_filter = ['is_valid', 'module']
    search_fields = ['certificate_number', 'user__username']
    readonly_fields = ['certificate_number', 'issued_at']
