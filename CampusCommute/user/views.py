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
def register_user(request):
    email_entered = request.POST['email']
    password_entered = request.POST['password']
    username_entered = request.POST['username']
        
    user = create_user(request, email=email_entered, username = username_entered, password=password_entered)
        
    if user is not None:
        user(request, user)
        return redirect('dashboard')
    else:
        return render(request, 'register.html', {'error': 'Invalid credentials'})
            
    return render(request, 'login.html')