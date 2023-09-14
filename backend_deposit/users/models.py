from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager


class User(AbstractUser):
    USER = "user"
    STAFF = "staff"
    ADMIN = "admin"
    ROLES = (
        (USER, "Пользователь"),
        (ADMIN, "Администратор"),
        (STAFF, "Персонал"),
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=30,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        null=True,
        blank=True
    )
    email = models.EmailField(
        verbose_name="Email-адрес",
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default=USER,
    )

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(
        verbose_name="Пользователь", to=User, on_delete=models.CASCADE
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=30,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        null=True,
        blank=True
    )
    email = models.EmailField(
        verbose_name="Email-адрес",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
