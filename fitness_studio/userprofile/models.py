from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models

choices=(
    ('admin', 'Admin'),
    ('member', 'Member'),
    ('trainer', 'Trainer'),
)

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE,related_name='profile')
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role=models.CharField(max_length=10, choices=choices, default='member')

    def __str__(self):
        return self.user.username