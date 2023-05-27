from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки отображения данных таблицы User."""
    list_display = ('id', 'first_name', 'last_name', 'email', 'username')
    list_filter = ('email', 'username')


admin.site.register(Subscription)
