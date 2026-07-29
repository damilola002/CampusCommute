from django.db import models
from django.contrib.auth.models import AbstractUser 

# Create your models here.
class CustomerUser(AbstractUser):
    full_name = models.CharField(max_length = 225)
    email = models.EmailField(unique=True) 
    
    USERNAME_FIELD = 'UTA Email'
    REQUIRED_FIELDS = ['Full Name']