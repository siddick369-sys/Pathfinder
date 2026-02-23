from django.urls import path
from . import views

app_name = 'competences'

urlpatterns = [
    path('', views.competences_list, name='list'),
    path('<slug:slug>/', views.apprentissage_view, name='apprentissage'),
    path('<slug:slug>/ressource/<int:resource_id>/', views.resource_detail_view, name='resource_detail'),
    path('<slug:slug>/ressource/<int:resource_id>/complete/', views.complete_resource, name='complete_resource'),
]
