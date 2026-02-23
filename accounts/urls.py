from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.register_view, name='register'),
    path('connexion/', views.login_view, name='login'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
