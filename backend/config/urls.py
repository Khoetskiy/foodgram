from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import config.settings

from apps.core.constants import SHORT_LINK_PREFIX
from apps.recipes.views import redirect_to_recipe

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
    path(
        f'{SHORT_LINK_PREFIX}/<str:short_code>/',
        redirect_to_recipe,
        name='short-link-redirect',
    ),
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
        ),
    )
