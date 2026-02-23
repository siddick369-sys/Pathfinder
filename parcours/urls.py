from django.urls import path
from . import views

app_name = 'parcours'

urlpatterns = [
    path('', views.career_view, name='career'),
    path('complete/<int:step_id>/', views.complete_step, name='complete_step'),
]
