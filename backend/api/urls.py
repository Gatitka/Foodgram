from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, MyUserViewSet, RecipeViewSet, TagViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('users', MyUserViewSet)

v1_router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
v1_router.register(
    'tags',
    TagViewSet,
    basename='tags'
)
v1_router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingridients'
)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
