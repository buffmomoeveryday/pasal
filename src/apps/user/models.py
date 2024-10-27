from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(verbose_name="email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str_(self):
        return self.email
