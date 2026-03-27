from django.urls import path
from . import views

app_name = 'orientation'

urlpatterns = [
    path('', views.test_view, name='test'),
    path('resultats/', views.results_view, name='results'),
    path('mini-quiz/', views.mini_quiz_view, name='mini_quiz'),
]
