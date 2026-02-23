from django.contrib import admin
from .models import CareerPath, CareerStep


class StepInline(admin.TabularInline):
    model = CareerStep
    extra = 1
    ordering = ('order',)


@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [StepInline]


@admin.register(CareerStep)
class CareerStepAdmin(admin.ModelAdmin):
    list_display = ('career', 'order', 'title', 'is_free', 'price_fcfa', 'is_premium')
    list_filter = ('career', 'is_free', 'is_premium')
