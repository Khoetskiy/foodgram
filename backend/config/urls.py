from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import config.settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
]


if config.settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        config.settings.MEDIA_URL, document_root=config.settings.MEDIA_ROOT
    )
    urlpatterns += (
        path(
            'api-auth/',
            include('rest_framework.urls', namespace='rest_framework'),
        ),  # FIXME: Для SessionAuthentication. Отключить на проде?
    )
