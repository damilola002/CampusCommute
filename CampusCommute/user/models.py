from django.db import models
from django.contrib.auth.models import AbstractUser 

# Create your models here.
class CustomerUser(AbstractUser):
    full_name = models.CharField("Enter full name", max_length = 225)
    email = models.EmailField("Enter email .edu", unique=True) 
    user = models.CharField("Username", max_length=225)
