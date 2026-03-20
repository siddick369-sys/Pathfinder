from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_dashboard, name='dashboard'),
    path('pointer-arrivee/', views.checkin, name='checkin'),
    path('pointer-depart/', views.checkout, name='checkout'),
    path('conges/', views.my_leaves, name='my_leaves'),
    path('conges/demande/', views.leave_request_create, name='leave_request'),
    path('historique/', views.attendance_history, name='history'),
]
