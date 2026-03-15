from django.contrib import admin
from .models import ServiceCategory, ServiceListing, Mission, MissionProposal, ServiceReview


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ServiceListing)
class ServiceListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'category', 'price_fcfa', 'status', 'total_orders', 'average_rating']
    list_filter = ['status', 'category']
    search_fields = ['title', 'provider__first_name']


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'category', 'budget_fcfa', 'deadline', 'status', 'assigned_to']
    list_filter = ['status', 'category']
    date_hierarchy = 'deadline'


@admin.register(MissionProposal)
class MissionProposalAdmin(admin.ModelAdmin):
    list_display = ['provider', 'mission', 'proposed_price_fcfa', 'status', 'created_at']
    list_filter = ['status']


@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'provider', 'rating', 'created_at']
    list_filter = ['rating']
