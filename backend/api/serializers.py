import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F, QuerySet
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from foodgram.settings import DEFAULT_RECIPES_LIMIT
from recipe.models import (Favorit, Ingredient, Recipe, RecipeIngredient,
                           RecipeTag, ShoppingCartUser, Tag)
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from user.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для модели User.
    Все поля обязательны
    Валидация:
    1) проверка, что переданный username не 'me';
    2) проверка уникальности полей email и username по БД.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed',
                  )
        model = User

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Использовать 'me' в качестве username запрещено."
            )
        return value

    def get_is_subscribed(self, obj) -> bool:
        """Проверка подписки пользователей.

        Определяет - подписан ли текущий пользователь
        на просматриваемого пользователя.

        Args:
            obj (User): Пользователь, на которого проверяется подписка.

        Returns:
            bool: True, если подписка есть. Во всех остальных случаях False.
        """
        request = self.context['request']
        return Subscription.objects.filter(
            user=request.user.id,
            author=obj.id
        ).exists()


class SignUpSerializer(UserSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Все поля обязательны.
    Валидация:
     - Если в БД есть пользователи с переданными email или username,
    вызывается ошибка.
     - Если имя пользователя - me, вызывается ошибка.
    """
    email = serializers.EmailField(
        max_length=254,
        required=True
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        min_length=8
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        max_length=150,
        min_length=8
    )

    class Meta:
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'password')
        read_only_fields = ('id',)
        model = User

    def validate(self, data):
        username = data['username']
        email = data['email']
        password = data['password']
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует."
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        if password is None:
            raise serializers.ValidationError(
                "Придумайте пароль."
            )
        return data

    def create(self, validated_data: dict) -> User:
        """ Создаёт нового пользователя с запрошенными полями.
        Args:
            validated_data (dict): Полученные проверенные данные.
        Returns:
            User: Созданный пользователь.
        """
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(UserSerializer):
    """
    Сериализатор для получения и изменения данных
    собственной учётной записи.
    Пользователь может узнать свою роль в системе, но не может её изменять.
    """

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role', 'is_subscribed')


class PasswordSerializer(serializers.Serializer):
    """
    Сериалайзер для данных, получаемях для смены пароля
    актуального пользователя.
    """
    new_password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.initial_data['user']
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Введен неверный текущий пароль.'
            )
        return value

    def validate_new_password(self, value):
        if value == self.initial_data['current_password']:
            raise serializers.ValidationError(
                'Новый пароль должен отличаться от старого!'
            )
        return value


class RecipesShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого отображения данных о подписках.
    """
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'image', 'cooking_time', 'name')
        model = Recipe
        read_only_fields = ('id', 'image', 'cooking_time', 'name')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения данных о рецептах и их авторов, находящихся
    в подписках у актуального пользователя.
    """
    recipes = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count',
                  )
        model = User

    def get_recipes(self, obj) -> QuerySet:
        """ Получает список рецептов автора, на которого оформлена подписка
        и возвращает кол-во, переданное в параметр запроса recipes_limit,
        переданного в URL.
        Args:
            user (User): Автор на которого подписан пользователь.
        Returns:
            QuerySet: список рецептов автора из подписки.
        """
        recipes_limit = self.context['recipes_limit']
        if recipes_limit is None:
            recipes_limit = DEFAULT_RECIPES_LIMIT
        else:
            recipes_limit = int(recipes_limit)
        serializer = RecipesShortSerializer(
            obj.recipes.all()[:recipes_limit],
            many=True
        )
        return serializer.data

    def get_is_subscribed(self, obj) -> bool:
        """Получает список подписок на авторизованного пользователя.
        Args:
            user (User): Автор на которого подписан пользователь.
        Returns:
            bool: есть подписка или нет.
        """
        current_user = self.context['current_user']
        return Subscription.objects.filter(
            user=current_user.id,
            author=obj.id
        ).exists()

    def get_recipes_count(self, obj) -> int:
        """Получает количество рецептов всех подписанных авторов.
        Args:
            obj (User): автор, на которого подписан пользователь.
        Returns:
            int: Колличество рецептов автора из подписки пользователя.
        """
        return obj.recipes_count


class TagSerializer(serializers.ModelSerializer):
    """ Сериалайзер тэга."""
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериалайзер ингредиентов."""
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериалайзер для рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField()
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author',
                  'name', 'image', 'text', 'cooking_time',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart'
                  )
        model = Recipe

    def get_ingredients(self, recipe: Recipe) -> QuerySet[dict]:
        """Получает список ингридиентов для рецепта.

        Args:
            recipe (Recipe): Запрошенный рецепт.

        Returns:
            QuerySet[dict]: Список ингридиентов в рецепте.
        """
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe__amount')
        )

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Получает булевое значение, если авторизованный пользователь имеет
        этот рецепт в избранном.
        Args:
            recipe (Recipe): Запрошенный рецепт.
        Returns:
            bool: в избранных или нет.
        """
        request = self.context['request']
        return Favorit.objects.filter(
            favoriter=request.user.id,
            recipe=recipe.id
        ).exists()

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """Получает булевое значение, если авторизованный пользователь имеет
        этот рецепт в корзине покупок.
        Args:
            recipe (Recipe): Запрошенный рецепт.
        Returns:
            bool: в корзине покупок или нет.
        """
        request = self.context['request']
        return ShoppingCartUser.objects.filter(
            owner=request.user.id,
            recipe=recipe.id
        ).exists()

    def to_internal_value(self, data):
        """
        Проверка данных, введенных в полях ingredients, tags.
        Обработка изображения для сохранения в БД.
        """
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if ingredients is None:
            raise serializers.ValidationError({
                'ingredients': 'Поле ingredients обязательно.'
            })
        if len(ingredients) == 0:
            raise serializers.ValidationError({
                'ingredients': 'Добавьте хотя бы 1 ингредиент.'
            })
        ingr_id_list = []
        for ingredient in ingredients:
            if "id" not in ingredient.keys():
                raise serializers.ValidationError({
                    'ingredients':
                        f'Отсутствует id ингредиента. {ingredient}'
                })
            if "amount" not in ingredient.keys():
                raise serializers.ValidationError({
                    'ingredients':
                        f'Отсутствует количество ингредиента {ingredient}.'
                })
            if ingredient['id'] in ingr_id_list:
                raise serializers.ValidationError({
                    "ingredients": [
                        'Проверьте список ингредиентов на повторение.'
                    ]
                })
            ingr_id_list.append(ingredient['id'])

        if tags is None:
            raise serializers.ValidationError({
                'tags': 'Поле tags обязательно.'
            })
        if len(tags) == 0:
            raise serializers.ValidationError({
                'tags': 'Добавьте хотя бы 1 тэг.'
            })

        image = data.get('image')
        if isinstance(image, str) and image.startswith('data:image'):
            format, imgstr = image.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            data['image'] = image

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        request = self.context['request']
        recipe = Recipe.objects.create(**validated_data, author=request.user)
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(Ingredient,
                                                   id=ingredient['id']
                                                   )
            RecipeIngredient.objects.create(
                ingredient=current_ingredient,
                amount=ingredient['amount'],
                recipe=recipe)
        for tag in tags:
            current_tag = get_object_or_404(Tag,
                                            id=tag
                                            )
            RecipeTag.objects.create(
                tag=current_tag,
                recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)

        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            instance.ingredients.clear()
            lst_ingrd = [
                RecipeIngredient(
                    ingredient=get_object_or_404(
                        Ingredient,
                        id=ingredient['id']
                    ),
                    amount=ingredient['amount'],
                    recipe=instance,
                )
                for ingredient in ingredients_data
            ]
            RecipeIngredient.objects.bulk_create(lst_ingrd)

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            lst_tag = []
            for tag in tags_data:
                current_tag = get_object_or_404(Tag, id=tag)
                lst_tag.append(current_tag)
            instance.tags.set(lst_tag)

        instance.save()
        return instance
