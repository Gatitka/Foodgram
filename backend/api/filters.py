from django_filters import FilterSet, NumberFilter
from django_filters import filters as df_f
from recipe.models import Ingredient, Recipe
from rest_framework import filters as rf_f


class CharFilter(df_f.BaseInFilter, df_f.CharFilter):
    pass


class RecipeFilter(FilterSet):
    """
    Кастомный фильтр фильтрует Queryset на основе query_params:
        Фильтры для всех пользователей:
            tags - рецепты с запрошенным тэгом
            authors - рецепты запрошенного автора

        Фильтры для авторизованых пользователей:
            is_favorited - рецепты находящиеся в избранном
                у текущего пользователя
            is_in_shopping_cart - рецепты, находящихся в корзине
                текущего пользователя
    """

    tags = CharFilter(field_name='tags__slug', lookup_expr='in')
    is_favorited = NumberFilter(field_name='favorited',    # поле в модели
                                method='filter_favorited')
    is_in_shopping_cart = NumberFilter(field_name='in_shopping_cart',
                                       method='filter_in_shopping_cart')

    def filter_favorited(self, queryset, name, value):

        if self.request.user.is_authenticated and value == 1:
            return queryset.filter(favorited__favoriter=self.request.user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value == 1:
            return queryset.filter(in_shopping_cart__owner=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'favorited', 'in_shopping_cart']


class IngredientFilter(rf_f.SearchFilter):
    """ Фильтр ингредиентов. """
    search_param = 'name'

    def filter_queryset(self, request, queryset, view):
        search_value = request.query_params.get(self.search_param, '')
        if search_value:
            queryset = queryset.filter(Q(name__startswith=search_value))
        return queryset
    # class Meta:
    #     model = Ingredient
    #     fields = ['name']
