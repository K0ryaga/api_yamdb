from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    confirmation_code = models.CharField(max_length=10)
    username = models.CharField(max_length=255, blank=True, unique=True)
    email = models.EmailField(max_length=255, blank=True, unique=True)

    def __str__(self):
        return self.username
