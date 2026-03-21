from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'PathFinder Admin'
admin.site.site_title = 'PathFinder'
admin.site.index_title = 'Tableau de bord administrateur'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('orientation/', include('orientation.urls')),
    path('parcours/', include('parcours.urls')),
    path('competences/', include('competences.urls')),
    path('paiement/', include('payments.urls')),
    path('gamification/', include('gamification.urls')),
    path('blog/', include('blog.urls')),
    path('notifications/', include('notifications.urls')),
    path('feedback/', include('feedback.urls')),
    path('formations/', include('learning.urls')),
    path('presences/', include('attendance.urls')),
    path('inventaire/', include('inventory.urls', namespace='inventory')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
