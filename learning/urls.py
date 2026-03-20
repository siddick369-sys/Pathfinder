from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.module_list, name='list'),
    path('mon-apprentissage/', views.my_learning, name='my_learning'),
    path('<slug:slug>/', views.module_detail, name='module_detail'),
    path('<slug:slug>/inscription/', views.enroll_module, name='enroll'),
    path('<slug:module_slug>/lecon/<int:lesson_id>/', views.lesson_view, name='lesson'),
    path('certificat/<str:cert_number>/', views.certificate_view, name='certificate'),
]
