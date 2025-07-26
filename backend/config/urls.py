from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import config.settings

urlpatterns = [
    path('admin/', admin.site.urls),
]

if config.settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
    urlpatterns += static(
        config.settings.MEDIA_URL, document_root=config.settings.MEDIA_ROOT
    )
