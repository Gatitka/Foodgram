from django.contrib import admin

from .forms import RecipeForm
from .models import (Favorit, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCartUser, Tag)


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient


class RecipeTagAdmin(admin.TabularInline):
    model = RecipeTag


admin.site.register(Tag)
admin.site.register(ShoppingCartUser)


@admin.register(Favorit)
class FavoritAdmin(admin.ModelAdmin):
    """Настройки отображения данных таблицы Recipe."""
    list_display = ('favoriter_id', 'favoriter', 'recipe_id', 'recipe')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения данных таблицы Recipe."""
    list_display = ('pk', 'name', 'author', 'in_favorits')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    inlines = (RecipeIngredientAdmin, RecipeTagAdmin,)
    form = RecipeForm

    def in_favorits(self, obj):
        return Favorit.objects.filter(recipe=obj).count()
    in_favorits.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения данных таблицы Ingredient."""
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
