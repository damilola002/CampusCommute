from django.db import models

class Ride(models.Model):
    pickup_location = models.CharField(max_length = 101)
    destination = models.CharField(max_length = 101)
    date = models.DateField()
    time = models.TimeField()
    seats_available = models.IntegerField()
