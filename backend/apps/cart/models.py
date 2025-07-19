from django.contrib.auth import get_user_model
from django.db import models

from apps.core.models import TimeStampModel
from apps.recipes.models import Recipe

User = get_user_model()


class Cart(TimeStampModel):
    """
    Модель корзины, привязанной к пользователю.
    Каждому пользователю соответствует одна корзина.
    """

    user = models.OneToOneField(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        help_text='Пользователь, к которому привязана эта корзина',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'объект "корзина"'
        verbose_name_plural = 'корзины'
        default_related_name = 'cart'

    def __str__(self) -> str:
        return f'Корзина пользователя: {self.user}'


class CartItem(TimeStampModel):
    """
    Модель элемента корзины.
    Один CartItem относится к одной Cart и одному Recipe.
    """

    cart = models.ForeignKey(
        Cart,
        verbose_name='корзина',
        on_delete=models.CASCADE,
        help_text='Корзина, к которой относится этот элемент',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        help_text='Рецепт, добавленный в корзину',
    )

    class Meta(TimeStampModel.Meta):
        verbose_name = 'элемент корзины'
        verbose_name_plural = 'элементы корзины'
        default_related_name = 'items'
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=['cart', 'recipe'], name='unique_cart_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'{self.recipe} в корзине {self.cart.user}'
