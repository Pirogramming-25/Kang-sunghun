from django.db import models
from django.contrib.auth.models import AbstractUser

# 소개글
class User(AbstractUser):
    nickname = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    bio = models.TextField(blank=True)
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
