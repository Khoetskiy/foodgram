# ruff: noqa: RUF012
from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import TimeStampModel
from apps.recipes.models import Recipe

User = get_user_model()


class Cart(TimeStampModel):
    """
    Модель корзины, привязанной к пользователю.
    Каждому пользователю соответствует одна корзина.

    Attributes:
        user (CustomUser): Пользователь, которому принадлежит корзина.
    """

    user = models.OneToOneField(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        help_text='Пользователь, к которому привязана эта корзина',
        related_name='cart',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'корзина'
        verbose_name_plural = 'корзины'
        indexes = [models.Index(fields=['user'], name='cart_user_idx')]

    def __str__(self) -> str:
        return f'Корзина пользователя: {str(self.user.username).upper()}'


class CartItem(TimeStampModel):
    """
    Элемент корзины: связь между корзиной и рецептом.

    Один CartItem связывает одну Cart с одним Recipe.

    Attributes:
        cart (Cart): Корзина, к которой относится этот элемент.
        recipe (Recipe): Рецепт, добавленный в корзину.
    """

    cart = models.ForeignKey(
        Cart,
        verbose_name='корзина',
        on_delete=models.CASCADE,
        help_text='Корзина, к которой относится этот элемент.',
        related_name='items',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        help_text='Рецепт, добавленный в корзину.',
        related_name='in_carts',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'элемент корзины'
        verbose_name_plural = 'элементы корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'recipe'], name='unique_cart_recipe'
            )
        ]
        indexes = [
            models.Index(fields=['cart'], name='cartitem_cart_idx'),
            models.Index(fields=['recipe'], name='cartitem_recipe_idx'),
        ]

    def __str__(self) -> str:
        return f'{self.recipe} в корзине {self.cart.user.username}'
