# Generated by Django 3.2.18 on 2023-06-05 12:57

import django.core.validators
from django.db import migrations, models
import recipe.validators


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(help_text='Оцените время, потраченное на приготовление рецепта.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время готовки'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Добавьте ингредиенты рецепта.', related_name='ingredient', through='recipe.RecipeIngredient', to='recipe.Ingredient', validators=[recipe.validators.recipe_has_ingredients], verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите тэги для рецепта.', through='recipe.RecipeTag', to='recipe.Tag', validators=[recipe.validators.recipe_has_tags], verbose_name='Тэг'),
        ),
    ]
