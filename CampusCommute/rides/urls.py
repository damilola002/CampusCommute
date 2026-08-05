from django.urls import path
from ...rides import views

urlpatterns = [
    path("offer-ride/", views.offer_ride),
    path("ride-request/", views.ride_request),
    path("create-ride-request/", views.create_ride_request, name="create_ride_request"),
    path("driver-requests/", views.driver_requests, name="driver_requests"),
    path("accept-request/<int:id>/", views.accept_request, name = "accept_request"),
]