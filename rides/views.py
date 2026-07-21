from django.shortcuts import render
from .models import Ride

def offer_ride(request):
    if request.method == "POST":
        Ride.objects.create(
            pickup_location = request.POST["pickup_location"],
            destination = request.POST["destination"],
            date = request.POST["date"],
            time = request.POST["time"],
            seats_available = request.POST["seats_available"]
        )
    return render (request,
                   "offer_ride.html")
