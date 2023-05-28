from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models


class UserRoles(models.TextChoices):
    ADMIN = ('admin', 'Администратор')
    USER = ('user', 'Пользователь')


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True
    )
    role = models.CharField(
        'Роль',
        max_length=9,
        choices=UserRoles.choices,
        default=UserRoles.USER
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    password = models.CharField(
        'Пароль',
        max_length=100,
        validators=[MinLengthValidator(8)]
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def is_admin(self):
        return self.role == UserRoles.ADMIN or self.is_superuser


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
        ]

    def clean(self):
        if self.user == self.author:
            raise ValidationError({'author':
                                   ['Подписываться на самого себя нельзя']})

    def __str__(self):
        return f'{self.user.id} {self.user} -> {self.user.id} {self.author}'
