from django import forms
from django.core.exceptions import ValidationError

from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'image', 'ingredients', 'author',
                  'text', 'tags', 'cooking_time']

    def clean(self):
        """
        Checks that all the words belong to the sentence's language.
        """
        ingredients = self.cleaned_data.get('ingredients')
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
                ingr_id_list.append(ingredient['id'])
                # db_ings = get_object_or_404(Ingredient, id=ingredient['id'])
                # ingr_id_list.append(db_ings.id)
        return self.cleaned_data
