from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import Ingredient, Tag


def recipe_has_ingredients(value):
    """ Валидация ингредиентов, добавляемых в рецепт."""
    ingredients = value
    if ingredients:
        if len(ingredients) == 0:
            raise ValidationError({
                'ingredients': 'Добавьте хотя бы 1 ингредиент.'
            })
        ingr_id_list = []
        for ingredient in ingredients:
            if "id" not in ingredient.keys():
                raise ValidationError({
                    'ingredients':
                    f'Отсутствует id ингредиента. {ingredient}'
                })
            if "amount" not in ingredient.keys():
                raise ValidationError({
                    'ingredients':
                    f'Отсутствует количество ингредиента {ingredient}.'
                })
            if ingredient['id'] in ingr_id_list:
                raise ValidationError({
                    "ingredients": [
                        'Проверьте список ингредиентов на повторение.'
                    ]
                })
            db_ings = get_object_or_404(Ingredient, id=ingredient['id'])
            ingr_id_list.append(db_ings.id)
        return value

    raise ValidationError({
        'ingredients': 'Поле ingredients обязательно.'
    })


def recipe_has_tags(value):
    tags = value
    if tags:
        if len(tags) == 0:
            raise ValidationError({
                'tags': 'Добавьте хотя бы 1 тэг.'
            })
        for tag in tags:
            if Tag.objects.filter(id=tag).exists():
                continue
            raise ValidationError({
                'tags': 'Такого тэга не существует.'
            })
        return value

    raise ValidationError({
        'tags': 'Поле tags обязательно.'
    })

#     year = value
#     if year:
#         if year > timezone.now().year:
#             raise ValidationError(
#                 'Дата публикации не может быть в будущем'
#             )
#         if year < 1895:
#             raise ValidationError(
#                 'Дата публикации не может быть '
#                 'раньше появления кинематографа'
#             )
#         return value
#     raise ValidationError(
#         'Необходимо указать год создания произведения'
#     )


# def validate_score(value):
#     """ Валидация оценки произведения в отзыве."""
#     score = value
#     if not (0 < score <= 10):
#         raise ValidationError('Оцените от 1 до 10.')
#     return value
