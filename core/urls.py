from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes (we keep adding here)
    path('api/auth/', include('accounts.urls')),
    path('api/events/', include('events.urls')), 
    path('api/tickets/', include('tickets.urls')),
    path('api/careerfair/', include('careerfair.urls')),
    path('api/stats/',      include('stats.urls')), 
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)