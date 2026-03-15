from django.urls import path
from . import views

app_name = 'mentorat'

urlpatterns = [
    path('', views.mentors_list, name='list'),
    path('mentor/<int:pk>/', views.mentor_detail, name='detail'),
    path('devenir-mentor/', views.become_mentor, name='become_mentor'),
    path('mon-profil/', views.my_mentor_profile, name='my_profile'),
    path('reserver/<int:mentor_id>/', views.book_session, name='book_session'),
    path('mes-sessions/', views.my_sessions, name='my_sessions'),
    path('session/<int:session_id>/terminer/', views.complete_session, name='complete_session'),
    path('groupe/<int:group_id>/rejoindre/', views.join_group, name='join_group'),
]
