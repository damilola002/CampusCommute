from django.shortcuts import render,redirect
from .models import Ride
from .models import RideRequest
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def offer_ride(request):
    if request.method == "POST":
        Ride.objects.create(
            pickup_location = request.POST["pickup_location"],
            destination = request.POST["destination"],
            date = request.POST["date"],
            time = request.POST["time"],
            seats_available = request.POST["seats_available"]
        )
        messages.success( request, "Your ride offer has been posted!!")
    return render (request,
                   "offer_ride.html")

def ride_request(request):
    search = request.GET.get("search")
    if search:
        rides = Ride.objects.filter(Q(destination__icontains=search) |
    Q(pickup_location__icontains=search)
)
    else:
        rides = Ride.objects.all()
        
    return render(request,"ride_request.html",{"rides": rides})

def create_ride_request(request):
    if request.method == "POST":
        ride_request = RideRequest.objects.create(  
            pickup_location = request.POST["pickup_location"],
            destination = request.POST["destination"],
            date = request.POST["date"],
            time = request.POST["time"],
            status = "Pending")
        return redirect("create_ride_request")
    return render(request, "create_ride_request.html")
@login_required
def driver_requests(request):
    ride_requests = RideRequest.objects.all()
    return render(request,"driver_request.html", {"ride_requests": ride_requests })

def accept_request(request,id):
    if request.method == "POST":
        ride_request = RideRequest.objects.get(id=id)
        ride_request.status = "Accepted"
        ride_request.save()
        messages.success( request, "Ride accepted successfully!!")
        return redirect("driver_requests")