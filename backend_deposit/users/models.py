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

    first_name = models.CharField(
        verbose_name="Имя",
        max_length=30,
        null=True
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
        null=True
    )
    email = models.EmailField(
        verbose_name="Email-адрес",
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

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = f"{self.first_name} {self.last_name}"
        return full_name

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff


class Profile(models.Model):
    user = models.OneToOneField(
        verbose_name="Пользователь", to=User, on_delete=models.CASCADE
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=30,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=150,
    )
    email = models.EmailField(
        verbose_name="Email-адрес",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
