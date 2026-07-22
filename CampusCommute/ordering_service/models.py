from django.db import models
from django.conf import settings 

# Create your models here.
class Ordering(models.Model):

    PENDING  = "PP"
    ACCEPTED = "AA"
    CANCELLED = "CC"
    STATUS_CHOICES = {
        PENDING: "Waiting on driver",
        ACCEPTED: "Accepted",
        CANCELLED: "Cancelled",
    }
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #create for driver
    #class Status(models.)
    