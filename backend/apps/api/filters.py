# from django_filters.rest_framework import FilterSet, filters
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget
from rest_framework.filters import SearchFilter

from apps.recipes.models import Recipe


# TODO: Refactoring!
class CustomSearchFilter(SearchFilter):
    # search_param = 'q'
    max_length = 50


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов по избранному, автору, корзине и тегам."""

    is_favorited = filters.TypedChoiceFilter(
        choices=((0, 'Нет'), (1, 'Да')),
        coerce=int,
        method='filter_is_favorited',
        label='В избранном?',
    )
    is_in_shopping_cart = filters.TypedChoiceFilter(
        choices=((0, 'Нет'), (1, 'Да')),
        coerce=int,
        method='filter_is_in_shopping_cart',
        label='В корзине?',
    )
    author = filters.NumberFilter()
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        if value == 1:
            return queryset.filter(favorited_by__favorite__user=user)
        return queryset.exclude(favorited_by__favorite__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none() if value else queryset
        if value == 1:
            return queryset.filter(in_carts__cart__user=user)
        return queryset.exclude(in_carts__cart__user=user)
