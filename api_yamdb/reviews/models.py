from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(unique=True, max_length=150)
    confirmation_code = models.CharField(max_length=10)

    def __str__(self):
        return self.username
