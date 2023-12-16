from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Title(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.title}"
