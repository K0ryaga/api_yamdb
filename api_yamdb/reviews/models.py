from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


from users.models import User

MAX_TEXT_LENGTH = 15


class Category(models.Model):
    name = models.CharField('Название', unique=True, max_length=256)
    slug = models.SlugField('Слаг', unique=True, max_length=50)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('slug',)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    name = models.CharField('Название', unique=True, max_length=256)
    slug = models.SlugField('Слаг', unique=True, max_length=50)

    def clean(self):
        existing_genres = Genre.objects.filter(slug=self.slug)
        if self.pk:
            existing_genres = existing_genres.exclude(pk=self.pk)
        if existing_genres.exists():
            raise ValidationError('Жанр с таким slug уже существует.')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('slug',)

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    year = models.IntegerField(
        verbose_name='Год выпуска',
        validators=[
            MaxValueValidator(
                timezone.now().year,
                'Нельзя добавлять произведения, которые еще не вышли.',
            ),
            MinValueValidator(
                1,
                'Нельзя добавлять произведения, с годом меньше 1.',
            ),
        ],
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        db_index=True
    )
    text = models.TextField(
        'Текст отзыва',
        help_text='Напишите свой отзыв.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
        db_index=True
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(1, 'Минимум 1'),
            MaxValueValidator(10, 'Максимум 10')
        ),
        help_text='Дайте оценку произведению.',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_title_author'
            ),
        )
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
        db_index=True
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
        db_index=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
