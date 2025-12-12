from django.contrib.auth.models import AbstractUser
from django.db import models
from dashboard.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.name if self.name else self.email
