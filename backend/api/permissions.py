from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Выполнение запросов запрещено для всех, кроме пользователей
    с ролью 'admin' или суперюзеров.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_admin():
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Методы GET, HEAD и OPTIONS доступны для всех пользователей (и анонимов).
    Добавлять, редактировать и удалять (методы POST, PUT, PATCH, DELETE)
    записи могут только пользователи с ролью 'admin' или суперюзеры.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and request.user.is_admin():
            return True
        return False


class IsAuthorAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Без авторизации доступны только запросы на чтение, для создания новой
    записи пользователь должен быть авторизован.
    Редактировать или удалять записи может только их автор или
    админ с модератором.
    """
    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve' or obj.author == request.user:
            return True
        if request.user.is_admin():
            return True
        return False
