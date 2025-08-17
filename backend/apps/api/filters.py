from django_filters import rest_framework as filters

from apps.recipes.models import Ingredient, Recipe

FILTER_CHOICES = (
    (0, 'Нет'),
    (1, 'Да'),
)


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов, позволяющий осуществлять поиск по названию."""

    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """
    Фильтр для рецептов по избранному, корзине, автору и тегам.

    Поддерживаемые фильтры:
    - is_favorited: фильтр по рецептам в избранном пользователя
    - is_in_shopping_cart: фильтр по рецептам в корзине пользователя
    - author: фильтр по ID автора рецепта
    - tags: фильтр по тегам (поддерживает множественный выбор)

    Примеры использования:
    - `/recipes/?is_favorited=1` - только избранные рецепты
    - `/recipes/?tags=breakfast,dinner` - рецепты c тегами
    - `/recipes/?author=5` - рецепты автора c ID=5
    """

    is_favorited = filters.TypedChoiceFilter(
        choices=FILTER_CHOICES,
        coerce=int,
        method='filter_is_favorited',
        label='В избранном?',
        help_text='Только рецепты добавленные в избранное',
    )
    is_in_shopping_cart = filters.TypedChoiceFilter(
        choices=FILTER_CHOICES,
        coerce=int,
        method='filter_is_in_shopping_cart',
        label='В корзине?',
        help_text='Только рецепты добавленные в корзину',
    )
    author = filters.NumberFilter(label='Автор', help_text='ID автора рецепта')
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Теги',
        help_text='Список доступных тегов',
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты по статусу "в избранном" для текущего пользователя.
        """
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none() if value else queryset

        if (
            value == 1
        ):  # REVIEW: Можно убрать сравнение и оставить только if value:()
            return queryset.filter(favorited_by__favorite__user=user)
        return queryset.exclude(favorited_by__favorite__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты по статусу "в корзине" для текущего пользователя.
        """
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none() if value else queryset

        if value == 1:
            return queryset.filter(in_carts__cart__user=user)
        return queryset.exclude(in_carts__cart__user=user)
