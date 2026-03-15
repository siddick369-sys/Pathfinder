from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_home, name='home'),
    path('service/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('publier-service/', views.create_listing, name='create_listing'),
    path('missions/', views.missions_list, name='missions'),
    path('mission/<int:pk>/', views.mission_detail, name='mission_detail'),
    path('publier-mission/', views.create_mission, name='create_mission'),
    path('mission/<int:pk>/postuler/', views.apply_mission, name='apply_mission'),
    path('candidature/<int:proposal_id>/accepter/', views.accept_proposal, name='accept_proposal'),
    path('mission/<int:pk>/terminer/', views.complete_mission, name='complete_mission'),
    path('mes-services/', views.my_services, name='my_services'),
]
