from django.db import models

class Ride(models.Model):
    pickup_location = models.CharField(max_length = 101)
    destination = models.CharField(max_length = 101)

    pickup_lat = models.FloatField(null=True, blank=True)

    pickup_lng = models.FloatField(null=True, blank=True)

    destination_lat = models.FloatField(null=True, blank=True)

    destination_lng = models.FloatField(null=True, blank=True)

    date = models.DateField()
    time = models.TimeField()
    seats_available = models.IntegerField()

class RideRequest(models.Model):
    pickup_location = models.CharField(max_length = 101)
    destination = models.CharField(max_length = 101)
    
    pickup_lat = models.FloatField(null=True, blank=True)

    pickup_lng = models.FloatField(null=True, blank=True)

    destination_lat = models.FloatField(null=True, blank=True)

    destination_lng = models.FloatField(null=True, blank=True)
    
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length = 20, default ="Pending")
