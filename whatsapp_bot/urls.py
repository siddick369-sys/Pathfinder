from django.urls import path
from . import views

app_name = 'whatsapp'

urlpatterns = [
    path('', views.whatsapp_dashboard, name='dashboard'),
    path('inscription/', views.subscribe_whatsapp, name='subscribe'),
    path('parametres/', views.toggle_whatsapp_settings, name='settings'),
    path('generer-partage/', views.generate_share_result, name='generate_share'),
    path('partage/<str:code>/', views.share_page, name='share_page'),
    path('micro-lecons/', views.micro_lessons_list, name='lessons'),
    path('webhook/', views.webhook_receive, name='webhook'),
]
