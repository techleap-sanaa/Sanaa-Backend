from django.db import models
from django.contrib.auth.models import AbstractUser

class AdminUser(AbstractUser):
    pass


class User(models.Model):
    """Details of the general user"""
    user_id = models.CharField(max_length=255, primary_key=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    primary_email = models.EmailField(max_length=255, blank=False, null=False, unique=True)
    phone_number = models.CharField(max_length=13)
    is_creator = models.BooleanField(default=False)
    is_signedin = models.BooleanField(default=False)
    created_at = models.CharField(max_length=255)
    updated_at = models.CharField(max_length=255)
    last_active_at = models.CharField(max_length=255)
    locked = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    profile_image = models.URLField(blank=False, null=False)
    two_factor_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.primary_email
    


