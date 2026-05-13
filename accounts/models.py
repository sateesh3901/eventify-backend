from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds role-based access and phone number field.
    """

    ROLE_CHOICES = (
        ('user', 'User'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'eventify_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_host(self):
        return self.role == 'host'

    @property
    def is_admin_user(self):
        return self.role == 'admin'