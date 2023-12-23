from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.mail import send_mail
from django.db.models import CharField

from .constants import (USER,
                        MODERATOR,
                        ADMIN,
                        CONF_CODE_MAX_LEN,
                        EMAIL_MAX_LEN,
                        ROLE_MAX_LEN,
                        USERNAME_MAX_LEN)
from .validators import username_validator, not_me_username_validator


class User(AbstractUser):
    """Модель Пользователя."""

    ROLE_CHOICES = (
        (USER, "user"),
        (MODERATOR, "moderator"),
        (ADMIN, "admin"),
    )

    bio = models.TextField(
        "Биография", blank=True, help_text="Здесь напишите о себе"
    )
    confirmation_code = models.CharField(
        "Код подтверждения", blank=True, max_length=CONF_CODE_MAX_LEN
    )
    email = models.EmailField(
        "Адрес эл. почты",
        max_length=EMAIL_MAX_LEN,
        blank=False,
        unique=True,
        help_text="Введите адрес электронной почты",
    )
    role = models.CharField(
        "Роль пользователя",
        choices=ROLE_CHOICES,
        max_length=ROLE_MAX_LEN,
        default="user",
        help_text="Выберите роль пользователя",
    )
    username = models.CharField(
        "Username",
        max_length=USERNAME_MAX_LEN,
        unique=True,
        help_text="Введите имя пользователя",
        validators=[not_me_username_validator, username_validator],
    )

    def email_user(
        self,
        message,
        subject="Регистрация",
        from_email="yamdb@gmail.com",
        **kwargs
    ):
        send_mail(
            subject,
            message,
            from_email,
            [self.email],
            fail_silently=False,
            **kwargs
        )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("id",)

    def __str__(self) -> CharField:
        return self.username

    def save(self, *args, **kwargs):
        if self.role == MODERATOR:
            self.is_staff = True
        if self.role == ADMIN:
            self.is_superuser = True
        super().save(*args, **kwargs)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN


class Category(models.Model):
    """Модель для категорий."""

    name = models.CharField("Наименование категории", max_length=256)
    slug = models.SlugField("Путь категории", max_length=50, unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("slug",)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Модель для жанров."""

    name = models.CharField("Наименование жанра", max_length=256)
    slug = models.SlugField("Путь жанра", max_length=50, unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ("id",)

    def __str__(self):
        return self.slug


class Title(models.Model):
    """Модель для произведений."""

    name = models.CharField("Наименование произведения", max_length=256)
    year = models.IntegerField(
        "Год выпуска",
        blank=True,
        validators=[MaxValueValidator(int(datetime.now().year))],
    )
    description = models.TextField("Описание", blank=True)
    genre = models.ManyToManyField(
        Genre,
        related_name="titles",
        verbose_name="Жанр",
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="titles",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ("id",)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для Отзыва+рейтинг."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name="Произведение",
        related_name="reviews",
    )
    text = models.TextField("Текст отзыва")
    score = models.PositiveSmallIntegerField(
        verbose_name="Оценка",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Ревью"
        verbose_name_plural = "Ревью"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                name="unique_review", fields=["author", "title"]
            ),
        ]

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    """Модель для Комментария к Отзыву."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField("Текст комментария")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("id",)

    def __str__(self):
        return self.text[:30]
