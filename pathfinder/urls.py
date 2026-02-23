from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.serve_html, name='home'),
    path('<str:page>.html', views.serve_html, name='html_pages'),
    re_path(r'^(?P<path>.*\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot|ico))$', serve, {
        'document_root': settings.BASE_DIR.parent,
    }),
]
