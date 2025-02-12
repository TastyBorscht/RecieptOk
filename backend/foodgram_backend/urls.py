from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from mypages.views import About, Technologies

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('about/', About.as_view(), name='about'),
    path('technologies/', Technologies.as_view(), name='technologies'),
    path('', include('api.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
