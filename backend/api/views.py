from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.db.models import Count, F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import Favorit, Ingredient, Recipe, ShopingCartUser, Tag
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from user.models import Subscription

from .filters import RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorAdminOrReadOnly
from .serializers import (IngredientSerializer, PasswordSerializer,
                          RecipeSerializer, RecipesShortSerializer,
                          SignUpSerializer, SubscriptionsSerializer,
                          TagSerializer, UserProfileSerializer)

User = get_user_model()


DATE_TIME_FORMAT = '%d/%m/%Y %H:%M'


class MyUserViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    Вьюсет модели User для отображения списка пользователей, создания
    нового пользователя, изменения пароля, просмотра конкретного
    пользователя, актуального пользователя (/me),
    страницы подписок (/subscriptions).

    """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    def get_instance(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return SignUpSerializer
        return self.serializer_class

    @action(
        detail=False,
        methods=['get'],
        serializer_class=UserProfileSerializer,
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def user_profile(self, request):
        """
        Экшен для обработки страницы актуального пользователя
        api/users/me.
        """
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request)
        return self.partial_update(request)

    @action(detail=False,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        """
        Экшен для обработки страницы смены пароля
        api/users/set_password.
        """
        user = request.user
        request.data['user'] = user
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(request.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated]
            )
    def subscriptions(self, request):
        """
        Экшен для обработки страницы подписок на авторов
        api/users/subscriptions.
        """
        queryset = User.objects.filter(
                   following__user=self.request.user
                   ).annotate(recipes_count=Count('recipes'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionsSerializer(page, many=True)
            serializer.context['current_user'] = request.user
            serializer.context[
                               'recipes_limit'
                              ] = request.query_params.get('recipes_limit')
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionsSerializer(queryset, many=True)
        serializer.context['current_user'] = request.user
        serializer.context[
                           'recipes_limit'
                           ] = request.query_params.get('recipes_limit')
        return Response(serializer.data)


class SubscribeViewSet(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """ Вьюсет модели User и работе с подписками. Создает или удаляет
    подписку актуального пользователя на автора, id которого преедается в
    url запросе.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionsSerializer

    def get_queryset(self,):
        return User.objects.filter(
            following__user=self.request.user
        ).annotate(recipes_count=Count('recipes'))

    def create(self, request, user_id=None):
        """
        Метод для создания подписки текущего пользователя на автора,
        заданного в url запросе.
        """
        current_user_id = request.user.id
        author = get_object_or_404(User, id=user_id)
        if self.request.user == author:
            return Response(f'{"Проверьте выбранного автора. "}'
                            f'{"Подписка на самого себя невозможна."}',
                            status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(
            user_id=current_user_id,
            author_id=user_id
        ).exists():
            return Response('Подписка на данного автора уже оформлена.',
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(
            user_id=current_user_id,
            author_id=user_id)
        return redirect('api:subscribe-detail',
                        user_id=current_user_id,
                        pk=user_id)

    def delete(self, request, user_id=None):
        current_user_id = request.user.id
        author = get_object_or_404(User, id=user_id)
        if not Subscription.objects.filter(user_id=current_user_id,
                                           author_id=author.id
                                           ).exists():
            return Response('Подписки на данного автора не существует.',
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.filter(user_id=current_user_id,
                                    author_id=author.id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """ Вьюсет модели Recipe, сериализатор подбирается по типу запроса."""
    permission_classes = [IsAuthorAdminOrReadOnly]
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.select_related(
                                    'author'
                                ).all(
                                ).prefetch_related(
                                    'tags', 'ingredients'
                                )

        if self.request.user.is_authenticated:

            is_favorited = self.request.query_params.get(
                'is_favorited'
                )

            if is_favorited is not None and is_favorited == '1':
                queryset = queryset.filter(
                    favorited__favoriter=self.request.user
                    )

            is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart'
                )

            if is_in_shopping_cart is not None and is_in_shopping_cart == '1':
                queryset = queryset.filter(
                        in_shoping_cart__owner=self.request.user
                    )
        return queryset

    @action(detail=True,
            methods=['post', 'delete'])
    def favorite(self, request, pk=None):

        current_user_id = request.user.id
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if Favorit.objects.filter(
                favoriter_id=current_user_id,
                recipe_id=recipe.id
            ).exists():
                return Response('Данный рецепт автора уже в избранном.',
                                status=status.HTTP_400_BAD_REQUEST)
            Favorit.objects.create(
                favoriter_id=current_user_id,
                recipe_id=recipe.id
                )
            return Response(RecipesShortSerializer(recipe).data)

        if request.method == 'DELETE':
            if not Favorit.objects.filter(
                favoriter_id=current_user_id,
                recipe_id=recipe.id
            ).exists():
                return Response('Данного рецепта нет в избранном.',
                                status=status.HTTP_400_BAD_REQUEST)
            Favorit.objects.filter(
                favoriter_id=current_user_id,
                recipe_id=recipe.id
                ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):

        current_user_id = request.user.id
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if ShopingCartUser.objects.filter(
                owner_id=current_user_id,
                recipe_id=recipe.id
            ).exists():
                return Response('Рецепт уже в корзине.',
                                status=status.HTTP_400_BAD_REQUEST)
            ShopingCartUser.objects.create(
                owner_id=current_user_id,
                recipe_id=recipe.id)
            return Response(RecipesShortSerializer(recipe).data)

        if request.method == 'DELETE':
            if not ShopingCartUser.objects.filter(
                owner_id=current_user_id,
                recipe_id=recipe.id
            ).exists():
                return Response('Данного рецепта нет в корзине.',
                                status=status.HTTP_400_BAD_REQUEST)
            ShopingCartUser.objects.filter(
                owner_id=current_user_id,
                recipe_id=recipe.id
                ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивает файл *.txt со списком покупок.

        Возвращает текстовый файл со списком ингредиентов из рецептов,
        добавленных в корзину для покупки.
        Колличесвто повторяющихся ингридиентов суммированно.
        Вызов метода через url:  */recipes/download_shopping_cart/.

        Args:
            request (WSGIRequest): Объект запроса.

        Returns:
            Responce: Ответ с текстовым файлом.
        """
        user = self.request.user
        if not ShopingCartUser.objects.filter(
                owner=user
                ).exists():
            return Response(
                'Корзина покупок пользователя пуста.',
                status=status.HTTP_400_BAD_REQUEST
                )

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для:\n\n{user.first_name}\n'
            f'Дата: {dt.now().strftime(DATE_TIME_FORMAT)}\n'
        ]

        ingredients = Ingredient.objects.filter(
            recipe__recipe__in_shoping_cart__owner=user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(amount=Sum('recipe__amount'))

        for ing in ingredients:
            shopping_list.append(
                f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
            )

        shopping_list.append('\nХороших покупок! Твой Foodgram')
        shopping_list = '\n'.join(shopping_list)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    def update(self, request, *args, **kwargs):
        if request.method == "PUT":
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().update(request, *args, **kwargs)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ Вьюсет модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ Вьюсет модели Ingredient."""
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name_search = self.request.query_params.get('name')
        queryset = Ingredient.objects.all()
        if name_search is not None:
            queryset = queryset.filter(name__startswith=name_search)
        return queryset
