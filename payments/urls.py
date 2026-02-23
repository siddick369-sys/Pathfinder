from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<str:item_type>/<int:item_id>/', views.payment_view, name='pay'),
    path('confirmation/', views.confirmation_view, name='confirmation'),
]
