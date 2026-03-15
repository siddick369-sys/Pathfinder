from django.urls import path
from . import views

app_name = 'parcours'

urlpatterns = [
    path('', views.career_view, name='career'),
    path('complete/<int:step_id>/', views.complete_step, name='complete_step'),
    path('projet/<int:step_id>/soumettre/', views.submit_project, name='submit_project'),
    path('projets/<int:step_id>/', views.projects_list, name='projects_list'),
    path('projet/<int:project_id>/evaluer/', views.review_project, name='review_project'),
    path('certificat/<str:code>/', views.certificate_view, name='certificate'),
]
