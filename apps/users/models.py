from django.contrib.auth.models import AbstractUser
from django.db import models


def user_image_path(instance, filename):
    """Build the path: users_images/user_<id>/<filename>"""
    return f"users_images/user_{instance.pk or 'new'}/{filename}"


class User(AbstractUser):
    image = models.ImageField(
        upload_to=user_image_path,
        blank=True,
        null=True,
        verbose_name="Аватар"
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField(max_length=100, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "user"
        verbose_name = "Користувача"
        verbose_name_plural = "Користувачі"

    def __str__(self):
        return self.username
