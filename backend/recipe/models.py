from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """ Тэги к рецептам. Один рецепт может иметь несколько тэгов.
    Тэги предустановлены."""
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='HEX',
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='slug',
        unique=True
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'
        ordering = ('name',)
        unique_together = ('name', 'color', 'slug')

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """ Модель для описания ингредиентов."""
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=24,
        db_index=True,
        verbose_name='Ед-ца измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id', )
        unique_together = ('name', 'measurement_unit')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Модель для описания рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
        help_text='Добавьте автора рецепта.'
    )
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название',
        help_text='Добавьте название готового блюда.'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        help_text='Добавьте изображение готового блюда.'
    )
    text = models.TextField(
        help_text='Введите способ приготовления.'
        )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='ingredient',
        help_text='Добавьте ингредиенты рецепта.'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тэг',
        help_text='Выберите тэги для рецепта.'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки',
        help_text='Оцените время, потраченное на приготовление рецепта.'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """ Модель для сопоставления связи рецепта и ингридиентов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент',
        related_name='recipe',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Кол-во'
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'рецепт-ингредиенты'
        verbose_name_plural = 'рецепты-ингредиенты'
        unique_together = ('recipe', 'ingredient')


class RecipeTag(models.Model):
    """ Модель для сопоставления связи рецепта и тэгов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.PROTECT,
        verbose_name='Тэг'
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'рецепт-тэг'
        verbose_name_plural = 'рецепты-тэги'
        unique_together = ('recipe', 'tag')


class Favorit(models.Model):
    """ Модель для добавления рецептов в избранное пользователя."""
    favoriter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorits',
        verbose_name='Избиратель'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited',
        verbose_name='Рецепты'
    )

    class Meta:
        ordering = ['favoriter']
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        unique_together = ('favoriter', 'recipe')

    def __str__(self):
        return f'{self.favoriter} -> {self.recipe}'


class ShopingCartUser(models.Model):
    """ Модель для добавления рецептов в корзину покупок."""
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        related_name='shoping_cart_owner',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shoping_cart',
        verbose_name='Рецепты'
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'корзина покупок'
        verbose_name_plural = 'корзины покупок'
        unique_together = ('owner', 'recipe')

    def __str__(self):
        return f'{self.owner} -> {self.recipe}'