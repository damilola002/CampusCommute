from django.urls import path
from . import views

urlpatterns = [
    path("offer-ride/", views.offer_ride),
]