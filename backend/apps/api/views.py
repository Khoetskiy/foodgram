from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.permissions import DenyAll, IsAdminOrReadOnly
from apps.api.serializers import (
    IngredientSerializer,
    PasswordSetSerializer,
    RecipeSerializer,
    TagSerializer,
    UserAvatarSerializer,
    UserCreateUpdateSerializer,
    UserReadSerializer,
)
from apps.core.constants import DISABLED_ACTIONS_DJOSER
from apps.recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class CustomUserViewSet(DjoserUserViewSet):
    """
    ViewSet для управления пользователями и получения информации о себе.

    Наследуется от UserViewSet Djoser.

    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserReadSerializer

    def get_permissions(self):
        if self.action in DISABLED_ACTIONS_DJOSER:
            return [DenyAll()]
        return super().get_permissions()

    def activation(self, request, *args, **kwargs):
        raise NotFound()

    # TODO: Переопределить так остальные ненужные actions


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_avatar(request):
    """Обработка изменения или удаления аватара текущего пользователя."""
    user = request.user

    if request.method == 'PUT':
        serializer = UserAvatarSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        if not user.avatar:
            return Response(
                {'detail': 'Аватар уже был удален.'},
                status=status.HTTP_204_NO_CONTENT,
            )
        user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=['avatar'])
        return Response(
            {'detail': 'Аватар успешно удален.'},
            status=status.HTTP_204_NO_CONTENT,
        )

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями и получения информации о себе."""

    queryset = User.objects.all().order_by('date_joined')
    # serializer_class = UserSerializer
    # permission_classes =
    # pagination_class =
    # throttle_classes =
    # http_method_names

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserReadSerializer

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,),
    )
    def current_user(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        url_name='me_avatar',
        permission_classes=(IsAuthenticated,),
        # serializer_class=UserAvatarSerializer,
    )
    def manage_avatar(self, request):
        instance = request.user

        if request.method == 'PUT':
            serializer = UserAvatarSerializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            if not instance.avatar:
                return Response(
                    {'detail': 'Аватар уже был удален.'},
                    status=status.HTTP_202_ACCEPTED,
                )
            instance.avatar.delete(save=False)
            instance.avatar = None
            instance.save(update_fields=['avatar'])
            return Response(
                {'detail': 'Аватар успешно удален.'},
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['post'],
        url_path='set_password',
        url_name='set_password',
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = PasswordSetSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {'detail': 'Пароль успешно изменён'}, status=status.HTTP_200_OK
        )


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet для получения информации o тегах."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None  # FIXME: вроде не надо по Redoc
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Ingredient.

    Поддерживает поиск по частичному вхождению в начале названия ингредиента.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
    pagination_class = None  # FIXME: вроде не надо по Redoc
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # filterset_fields = ('name',)
    search_fields = ('^name',)  # NOTE: ^ - startswith


# ===========================================================


class RecipeListView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeApiView(generics.ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


# class IngredientViewSet(viewsets.ModelViewSet):
#     # queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer

#     # def get_queryset(self):
#     #     return super().get_queryset()[:3]  # Обрезаю до 3 записей

#     def get_queryset(self):
#         pk = self.kwargs.get('pk')

#         if not pk:
#             return Ingredient.objects.all()[:3]

#         return Ingredient.objects.filter(
#             pk=pk
#         )  # NOTE: get_queryset должен возвращать список, поэтому filter а не get

#     # NOTE: Если переопределяем, то можем убрать атрибут класса queryset, но нужно `basename` в router

#     @action(methods=['get'], detail=False)
#     def get_recipes(self, request):
#         recipes = Recipe.objects.all()
#         return Response({'recipes': [i.name for i in recipes]})

#     @action(methods=['get'], detail=True)
#     def recipe(self, request, pk=None):
#         recipe = Recipe.objects.get(pk=pk)
#         return Response({'result': recipe.name})


class IngredientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientAPIUpdate(generics.UpdateAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientApiList(generics.ListCreateAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
    )  # EXAMPLE: Проверю права доступа


class IngredientApiView(APIView):
    def get(self, request):
        ingredients = Ingredient.objects.all()
        return Response(
            {'data': IngredientSerializer(ingredients, many=True).data}
        )

    # def get(self, request):
    # ingredients = Ingredient.objects.all().values()
    # return Response({'data': list(ingredients)})

    def post(self, request):
        serializer = IngredientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'data': serializer.data})

        # def post(self, request):
        #     new_ingredient = Ingredient.objects.create(
        #         name=request.data['name'],
        #         measurement_unit_id=request.data['measurement_unit_id'],
        #     )
        # return Response({'post': model_to_dict(new_ingredient)})

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        if not pk:
            return Response({'error': 'Method PUT not allowed'})

        try:
            instance = Ingredient.objects.get(pk=pk)
        except:
            return Response({'error': 'Object does ot exists'})

        serializer = IngredientSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data': serializer.data})

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        if not pk:
            return Response(
                {'error': 'Method DELETE not allowed'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        try:
            instance = Ingredient.objects.get(pk=pk)
        except Ingredient.DoesNotExist:
            return Response(
                {'error': 'Object does not exists'},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()

        return Response(
            {'data': f'delete object {pk}'},
            status=status.HTTP_204_NO_CONTENT,
        )
