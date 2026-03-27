from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='list'),
    path('ecrire/', views.create_post, name='create_post'),
    path('temoignages/', views.testimonials_list, name='testimonials'),
    path('temoigner/', views.create_testimonial, name='create_testimonial'),
    path('<slug:slug>/', views.blog_detail, name='detail'),
]
