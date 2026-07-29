from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

# Create your views here.
#creating the orders 
def orders(request):
    if request.method == "GET":
        user_order = request.POST.get('pickup_location')