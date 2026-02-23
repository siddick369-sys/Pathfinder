from django.contrib import admin
from .models import PaymentSimulation, UserProgress

@admin.register(PaymentSimulation)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_fcfa', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    date_hierarchy = 'created_at'

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'global_percent')
