from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
        ('O', 'سایر')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
