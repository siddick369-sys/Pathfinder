from django.contrib import admin
from .models import OrientationQuestion, OrientationChoice, OrientationResult


class ChoiceInline(admin.TabularInline):
    model = OrientationChoice
    extra = 4


@admin.register(OrientationQuestion)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'text', 'category')
    list_filter = ('category',)
    ordering = ('order',)
    inlines = [ChoiceInline]


@admin.register(OrientationResult)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommended_career', 'created_at')
    list_filter = ('recommended_career',)
    readonly_fields = ('scores', 'selected_choices', 'priority_skills')
