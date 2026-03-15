from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('boutique/', views.shop_view, name='shop'),
    path('classement/', views.leaderboard_view, name='leaderboard'),
    path('profil/', views.profile_gamification, name='profile'),
    path('convertir-xp/', views.convert_xp_to_discount, name='convert_xp'),
    path('parrainage/', views.referral_view, name='referral'),
]
