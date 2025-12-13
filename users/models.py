from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    image = models.ImageField(
        upload_to="users_images", blank=True, null=True, verbose_name="Аватар"
    )
    phone_number = models.CharField(max_length=10, blank=True, null=True)

    email = models.EmailField(max_length=100, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "user"
        verbose_name = "Користувача"
        verbose_name_plural = "Користувачі"

    def __str__(self):
        return self.username
