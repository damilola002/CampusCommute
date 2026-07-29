from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.contrib.auth import authenticate, AuthenticationForm, login
from .models import CustomerUser
from django.contrib.auth.models import User

def login_user(request):
    if request.method == "POST":
        email_entered = request.POST['email']
        password_entered = request.POST['password']
        
        user = authenticate(request, username=email_entered, password=password_entered)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
            
    return render(request, 'login.html')
    #bloom filter algotithim can be used for usernames and emails (anything unique), bit field
    # this is for the sign up to create a new user. 
def register_user(request):
    if request.method == "POST":
    
        email_entered = request.POST['email']
        password_entered = request.POST['password']
        username_entered = request.POST['username']
        
        user = CustomerUser.objects.create_user(username = username_entered, email = email_entered, password= password_entered)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'signup.html', {'error': 'Invalid credentials'})
         
    return render(request, 'signup.html')