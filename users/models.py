# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class User(AbstractUser):
    # username остаётся как в AbstractUser
    email = models.EmailField(_("email address"), unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Аватар")

    USERNAME_FIELD = "email"  # вход по email
    REQUIRED_FIELDS = ["username"]  # username обязателен при createsuperuser

    def __str__(self):
        return f"{self.username} ({self.email})"
