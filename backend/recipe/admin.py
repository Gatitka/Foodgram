from django.contrib import admin

from .models import (Favorit, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingCartUser, Tag)

admin.site.register(Tag)
admin.site.register(ShoppingCartUser)


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


class RecipeTagAdmin(admin.TabularInline):
    model = RecipeTag
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки отображения данных таблицы Recipe."""
    list_display = ('pk', 'name', 'author', 'in_favorits')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')
    inlines = (RecipeIngredientAdmin, RecipeTagAdmin,)

    def in_favorits(self, obj):
        return Favorit.objects.filter(recipe=obj).count()
    in_favorits.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения данных таблицы Ingredient."""
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
