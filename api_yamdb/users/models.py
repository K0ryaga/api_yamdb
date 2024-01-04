from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Переопределена модель User
    """
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    CHOICES_ROLE = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        'E-mail',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=150,
        default=USER,
        choices=CHOICES_ROLE,
    )
    confirmation_code = models.CharField(
        # Используйется для def sign_up
        # теперь не используется однако убрать нельзя ибо будут ошибки
        # нужно думать что с ней делать
        max_length=32,
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    def __str__(self) -> str:
        return self.username
