from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.api.routers import MyCustomRouter
from apps.api.views import (
    CustomUserViewSet,
    IngredientApiList,
    IngredientAPIUpdate,
    IngredientApiView,
    IngredientDetailAPIView,
    IngredientViewSet,
    RecipeApiView,
    RecipeListView,
    TagViewSet,
    UserViewSet,
    manage_avatar,
)

app_name = 'api_v1'

router_v1 = DefaultRouter()
router_v1.register(r'users', CustomUserViewSet, basename='users')
# router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')




# djoser_auth = [
#     # re_path(r'^auth/', include('djoser.urls')),
#     re_path(r'^auth/', include('djoser.urls.authtoken')),
# ]


v1_patterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', manage_avatar, name='manage_avatar'),
]


urlpatterns = [
    path('v1/', include(v1_patterns)),
]

# TODO: Сделать структуру путей
